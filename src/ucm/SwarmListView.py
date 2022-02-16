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

import logging
import os
import socket
import subprocess
import traceback
import time
from shlex import split

from urwid import Text, raw_display, Pile, ListBox, SimpleListWalker
from ucm.Widgets import ListView, ListItem
from ucm.Registry import Registry
from ucm.UserConfig import UserConfig
from ucm.Dialogs import DialogDisplay
from ucm.constants import MAIN_PALETTE


def host_is_local(hostname, port=None):
    """returns True if the hostname points to the localhost, otherwise False."""
    if port is None:
        port = 22  # no port specified, lets just use the ssh port
    hostname = socket.getfqdn(hostname)
    if hostname in ("localhost", "0.0.0.0", "127.0.0.1", "docker-desktop"):
        return True
    localhost = socket.gethostname()
    localaddrs = socket.getaddrinfo(localhost, port)
    targetaddrs = socket.getaddrinfo(hostname, port)
    for (family, socktype, proto, canonname, sockaddr) in localaddrs:
        for (rfamily, rsocktype, rproto, rcanonname, rsockaddr) in targetaddrs:
            if rsockaddr[0] == sockaddr[0]:
                return True
    return False


def build_ssh_command(host: str):
    connections = list(filter(lambda k: k['hostname'] == host, UserConfig().ssh_connections))
    if len(connections) == 1:
        data = connections[0]
        user_at_host = data['address'] if 'user' not in data else f"{data['user']}@{data['address']}"
        ident = f"-i {data['identity_file']}" if 'identity_file' in data else ''
        port = f"-p {data['port']}" if 'port' in data else ''
        opts = f"{data['options']}" if 'options' in data else ''
        return f"ssh {ident} {port} {opts} {user_at_host}"


# noinspection PyStatementEffect
def swarm_connect(data: any, shell: str = 'bash'):
    command = f"docker exec -it  {data['container']} {shell}"
    if not host_is_local(data['host']):
        command = f"{build_ssh_command(data['host'])} {command}"

    if Registry().get('main_loop'):
        Registry().main_loop.screen.stop()
        print(chr(27) + "[2J")
        print(command)
        logging.info(command)
        rc = os.system(command)
        if rc == 32256:
            rc = os.system(command.replace(" bash", " sh"))
        if rc != 0:
            print(f"Return code: {rc}")
            time.sleep(5)
        Registry().main_loop.screen.start(alternate_buffer=True)
        Registry().main_loop.screen.clear()


# noinspection PyStatementEffect
def swarm_inspect(data: any):

    command = f"{UserConfig().docker} inspect {data['container']}"
    if not host_is_local(data['host']):
        command = f"{build_ssh_command(data['host'])} {command}"

    proc = subprocess.Popen(split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return [Text(x.rstrip()) for x in proc.communicate()[0].splitlines()]


# noinspection PyStatementEffect
class SwarmListView(ListView):

    def __init__(self):
        super().__init__('Swarm', filter_fields=['stack', 'host', 'container'])

    def formatter(self, record: any):

        display_host = record['host'] if len(record['host']) <= 50 else f'...{record["host"][-37:]}'
        display_stack = record['stack'] if len(record['stack']) <= 20 else f'...{record["stack"][-17:]}'
        display_container = record['container'] if len(record['container']) <= 20 else f'{record["container"][0:37]}...'

        return f"{str(record['index']).ljust(3)}   {display_stack.ljust(20)}   {display_host.ljust(40)}   {display_container.ljust(40)}   {record['image']}"

    # noinspection PyMethodMayBeStatic
    def fetch_data(self):
        data = []
        # noinspection PyBroadException,PyPep8
        try:
            proc = subprocess.Popen(['bash', os.path.join(os.path.dirname(__file__), 'ucm-swarmlisting.sh')], stdout=subprocess.PIPE)
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                parts = line.decode('UTF-8').split()
                if 'CONTAINER' not in parts[0]:
                    data.append({'stack': parts[0].strip(), 'container': parts[1].strip(), 'host': parts[2].strip(), 'image': parts[3].strip()})
        except Exception as _e:
            logging.error(traceback.format_exc())

        return data

    def double_click_callback(self):
        logging.debug(f'{self.name}] {self.selected.item_data["container"]} double_click_callback')
        swarm_connect(self.selected.item_data)

    @staticmethod
    def popup_info_dialog(data):
        cols, rows = raw_display.Screen().get_cols_rows()
        d = DialogDisplay(f"Container Inpsection: {data['name']}", cols - 20, rows - 6,
                          body=Pile([
                              ListBox(
                                  SimpleListWalker(swarm_inspect(data))
                              )]),
                          loop=Registry().main_loop,
                          exit_cb=SwarmListView.close_cb,
                          palette=MAIN_PALETTE)
        d.add_buttons([("Cancel", 1)])
        d.show()

    @staticmethod
    def close_cb(button: any):
        pass

    def keypress_callback(self, size, key, list_item: ListItem = None):
        logging.debug(f'ListViewHandler[{self.name}] {size} {key} pressed')
        if key in ['c', 'b']:
            self.connect(list_item.item_data)
        elif key == 's':
            self.connect(list_item.item_data, shell='sh')

    def keypress_callback(self, size, key, data: any = None):
        logging.debug(f'ListViewHandler[{self.name}] {size} {key} pressed')
        if key == 'c':
            swarm_connect(data, shell='bash')
        if key == 'i':
            SwarmListView.popup_info_dialog(data)

    def get_header(self):
        return f"{'#'.ljust(3)}   {'Stack'.ljust(20)}   {'Host'.ljust(40)}   {'Container'.ljust(40)}   Image"

# vim: ts=4 sw=4 et
