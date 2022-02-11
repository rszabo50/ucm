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
from ucm.Widgets import ListView, ListItem


# noinspection PyStatementEffect
class SwarmListView(ListView):

    def __init__(self):
        super().__init__('Swarm', filter_fields=['stack', 'host', 'container'])

    def formatter(self, record: any):

        display_host = record['host'] if len(record['host']) <= 50 else f'...{record["host"][-47:]}'
        display_stack = record['stack'] if len(record['stack']) <= 20 else f'...{record["stack"][-17:]}'

        return f"{str(record['index']).ljust(3)}   {display_stack.ljust(20)}   {display_host.ljust(50)}   {record['container']}"

    # for s in $(docker stack ls --format '{{.Name}}'); do docker stack ps $s --format '{{.ID}}\t{{.Name}}\t{{.Node}}\t{{.Image}}' -f "desired-state=running" ;done

    @staticmethod
    def fetch_data():
        data = [
            {'stack': 'prod_data', 'host': 'PwP3-PSPC-DSB-BPS-GCAccounts-integration-swarm1-VM',
             'container': 'prod_data_ipd.324867ksdfj8sd'},
            {'stack': 'prod_data', 'host': 'PwP3-PSPC-DSB-BPS-GCAccounts-integration-swarm1-VM',
             'container': 'prod_data_user_datastore.324867ksdfj8sd'},
            {'stack': 'prod_data', 'host': 'PwP3-PSPC-DSB-BPS-GCAccounts-integration-swarm1-VM',
             'container': 'prod_data_am_datastore.324867ksdfj8sd'}
        ]
        return data

    def filter_data(self, filter_string: str):
        return list(
            filter(
                lambda k: filter_string.lower() in k['container'].lower() or filter_string.lower() in k['host'].lower(),
                self.fetch_data()))

    def double_click_callback(self):
        logging.debug(f'{self.name}] {self.selected.item_data["container"]} double_click_callback')
        self.connect(self.selected.item_data)

    def keypress_callback(self, size, key, list_item: ListItem = None):
        logging.debug(f'ListViewHandler[{self.name}] {size} {key} pressed')
        if key in ['c', 'b']:
            self.connect(list_item.item_data)
        elif key == 's':
            self.connect(list_item.item_data, shell='sh')

    def connect(self, data: any, shell: str = 'bash'):
        pass

    def get_header(self):
        return f"{'#'.ljust(3)}   {'Stack'.ljust(20)}   {'Host'.ljust(50)}   Container"

# vim: ts=4 sw=4 et
