#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#  Copyright (C) 2022 Robert Szabo.
#
#  This software can be used by anyone at no cost, however,
#  if you like using my software and can support - please
#  donate money to a children's hospital of your choice.
#  This program is free software: you can redistribute it
#  and/or modify it under the terms of the GNU General Public
#  License as published by the Free Software Foundation:
#  GNU GPLv3. You must include this entire text with your
#  distribution.
#  This program is distributed in the hope that it will be
#  useful, but WITHOUT ANY WARRANTY; without even the implied
#  warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#  PURPOSE.
#  See the GNU General Public License for more details.
#

# Created by rszabo50 at 2022-02-01

import subprocess
import traceback
import os
import time
import logging
from urwid import Columns, AttrWrap, Text, RIGHT, raw_display, Pile, ListBox, SimpleListWalker
from ucm.Widgets import ListView, ListItem
from ucm.Registry import Registry
from ucm.UserConfig import UserConfig
from ucm.Dialogs import DialogDisplay
from ucm.constants import MAIN_PALETTE


# noinspection PyStatementEffect
def docker_connect(data: any, shell: str = 'bash'):
    if Registry().get('main_loop'):
        Registry().main_loop.screen.stop()
        print(chr(27) + "[2J")
        print(f"Executing: {UserConfig().docker} exec -it  {data['name']} {shell}")
        logging.info(f"{UserConfig().docker} exec -it  {data['name']} {shell}")
        rc = os.system(f"{UserConfig().docker} exec -it  {data['name']} {shell}")
        if rc == 32256:
            rc = os.system(f"{UserConfig().docker} exec -it  {data['name']} sh")
        if rc != 0:
            print(f"Return code: {rc}")
            time.sleep(5)
        Registry().main_loop.screen.start(alternate_buffer=True)
        Registry().main_loop.screen.clear()


# noinspection PyStatementEffect
def docker_inspect(data: any):
    proc = subprocess.Popen([f"{UserConfig().docker}", "inspect", f"{data['name']}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return [Text(x.rstrip()) for x in proc.communicate()[0].splitlines()]


class DockerListView(ListView):

    def __init__(self):
        super().__init__('Docker', filter_fields=['containerId', 'name', 'image'])

    def formatter(self, record: any):
        return f"{str(record['index']).ljust(3)} {record['containerId'].ljust(15)} {record['name'].ljust(20)} {record['image']}"

    # noinspection PyMethodMayBeStatic
    def fetch_data(self):
        data = []
        # noinspection PyBroadException,PyPep8
        try:
            proc = subprocess.Popen(
                [UserConfig().docker, 'ps', '--format', 'table {{.ID}}\t{{.Names}}\t{{.Image}}'],
                stdout=subprocess.PIPE)
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                parts = line.decode('UTF-8').split()
                if 'CONTAINER' not in parts[0]:
                    data.append({'containerId': parts[0].strip(), 'name': parts[1].strip(), 'image': parts[2].strip()})
        except Exception as _e:
            logging.error(traceback.format_exc())

        return data

    @staticmethod
    def popup_info_dialog(data):
        cols, rows = raw_display.Screen().get_cols_rows()
        d = DialogDisplay(f"Container Inpsection: {data['name']}", cols - 20, rows - 6,
                          body=Pile([
                              ListBox(
                                  SimpleListWalker(docker_inspect(data))
                              )]),
                          loop=Registry().main_loop,
                          exit_cb=DockerListView.close_cb,
                          palette=MAIN_PALETTE)
        d.add_buttons([("Cancel", 1)])
        d.show()

    @staticmethod
    def close_cb(button: any):
        pass

    def double_click_callback(self):
        logging.debug(f'{self.name}] {self.selected.item_data["name"]} double_click_callback')
        connect(self.selected.item_data)

    def keypress_callback(self, size, key, data: any = None):
        logging.debug(f'ListViewHandler[{self.name}] {size} {key} pressed')
        if key == 'c':
            connect(data, shell='bash')
        if key == 'i':
            DockerListView.popup_info_dialog(data)

    def get_filter_widgets(self):
        return Columns([
            super().get_filter_widgets(),
            Columns([AttrWrap(Text("| On highlighted row: 'c' = connect", align=RIGHT), 'header', 'header')])
        ])

    def get_header(self):
        return f"{'#'.ljust(3)} {'ContainerId'.ljust(15)} {'Name'.ljust(20)} Image"

# vim: ts=4 sw=4 et
