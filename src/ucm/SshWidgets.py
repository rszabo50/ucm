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

import os
import time
import logging
from urwid import Columns, AttrWrap, Text, RIGHT, Pile, ListBox, SimpleListWalker
from ucm.Widgets import ListView
from ucm.UserConfig import UserConfig
from ucm.Registry import Registry
from ucm.constants import MAIN_PALETTE
from ucm.Dialogs import DialogDisplay


class SshListView(ListView):

    def __init__(self):
        super().__init__('SSH', filter_fields=['category', 'name', 'user', 'address'])

    def formatter(self, record: any):

        if 'category' not in record:
            record['category'] = '---'

        display_host = record['name'] if len(record['name']) <= 50 else f'...{record["name"][-47:]}'
        display_category = record['category'] if len(record['category']) <= 20 else f'...{record["category"][-20:]}'
        connection = record['address'] if 'user' not in record else f"{record['user']}@{record['address']}"

        return f"{str(record['index']).ljust(3)}   {display_category.ljust(20)}   {display_host.ljust(50)}   {connection}"

    @staticmethod
    def fetch_data():
        return UserConfig().get('ssh_connections')

    def double_click_callback(self):
        logging.debug(f'{self.name}] {self.selected.item_data["name"]} double_click_callback')
        self.connect(self.selected.item_data)

    def keypress_callback(self, size, key, data: any = None):
        logging.debug(f'ListViewHandler[{self.name}] {size} {key} pressed')
        if key == 'c':
            self.connect(data)
        if key == 'i':
            SshListView.popup_info_dialog(data)

    @staticmethod
    def popup_info_dialog(data):
        d = DialogDisplay(f"{data['name']}", 90, len(data.keys())+9,
                          body=Pile([
                              ListBox(
                                  SimpleListWalker([Text(f'{k.ljust(25)} : {v}') for k, v in data.items()])
                              )]),
                          loop=Registry().main_loop,
                          exit_cb=SshListView.close_cb,
                          palette=MAIN_PALETTE)
        d.add_buttons([("Cancel", 1)])
        d.show()

    @staticmethod
    def close_cb(button: any):
        pass

    def get_filter_widgets(self):
        return Columns([
            super().get_filter_widgets(),
            Columns([AttrWrap(Text("| On highlighted row: 'c' = connect, 'i' = info", align=RIGHT), 'header', 'header')])
        ])

    @staticmethod
    def build_ssh_command(data: dict):
        # - name: hostname
        #     address: ip or dns resolvable name
        #     user: username to connect with
        #     port: tcp port to use: default: 22
        #     identity: identity file to use if needed and its not your default key
        #     options: any other ssh options
        #     category: key to group  this buy, makes filtering easier

        user_at_host = data['address'] if 'user' not in data else f"{data['user']}@{data['address']}"
        ident = f"-i {data['identity_file']}" if 'identity_file' in data else ''
        port = f"-p {data['port']}" if 'port' in data else ''
        opts = f"{data['options']}" if 'options' in data else ''
        return f"ssh {ident} {port} {opts} {user_at_host}"

    def connect(self, data: any):
        if Registry().get('main_loop'):
            Registry().main_loop.screen.stop()
            print(chr(27) + "[2J")
            cmd = self.build_ssh_command(data)
            print(f"Executing: {cmd}")
            logging.info(f"{cmd}")
            rc = os.system(f"{cmd}")
            if rc != 0:
                print(f"Return code: {rc}")
                time.sleep(2)
            Registry().main_loop.screen.start(alternate_buffer=True)
            Registry().main_loop.screen.clear()

    def get_header(self):
        return f"{'#'.ljust(3)}   {'Category'.ljust(20)}   {'Hostname'.ljust(50)}   Connection"

# vim: ts=4 sw=4 et
