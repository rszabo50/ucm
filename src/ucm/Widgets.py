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

# Created by rszabo50 at 2022-01-28

import logging
import time
import re
import os

from urwid import AttrWrap, AttrMap, AttrSpec, Button, BoxAdapter, Columns, Divider, Edit, Filler, LineBox, ListBox, Padding, Pile, Text, WidgetWrap
from urwid import connect_signal, disconnect_signal, emit_signal, register_signal
from urwid import raw_display, SimpleFocusListWalker, SimpleListWalker
from urwid import CENTER, LEFT, RIGHT
from panwid.listbox import ScrollingListBox
from panwid.scroll import ScrollBar

from ucm.Registry import Registry


class IdWidget(AttrMap):
    def __init__(self, w: any, attr_map: any = None, focus_map: any = None, widget_id: str = None):
        super().__init__(w, attr_map, focus_map)
        base_id = widget_id
        if widget_id is not None:
            if hasattr(Registry(), widget_id):
                logging.warning(f"Registry already has object with widget_id={widget_id}")
                counter = 1
                while True:
                    widget_id = f'{base_id}_{counter}'
                    if not hasattr(Registry(), widget_id):
                        break
                    counter += 1
            logging.info(f"Registering widget with id={widget_id}")
            setattr(Registry(), widget_id, self)


class UCMScrollBar(ScrollBar):

    _thumb_char = ("light blue", "\u2588")
    _trough_char = ("dark blue", "\u2591")
    _thumb_indicator_top = ("white inverse", "\u234d")
    _thumb_indicator_bottom = ("white inverse", "\u2354")


class HeaderButton(Button):
    button_right = Text("")
    button_left = Text("")


class Clock(IdWidget):

    def __init__(self, widget_id: str = None):
        super().__init__(Text(time.strftime('%H:%M:%S'), align=RIGHT), widget_id=widget_id)

    def update_clock(self, _data: any = None, _other: any = None):
        self.original_widget.set_text(time.strftime('%H:%M:%S'))
        Registry().main_loop.set_alarm_in(1, self.update_clock)

    def start(self):
        Registry().main_loop.set_alarm_in(1, self.update_clock)


class Header(IdWidget):

    def __init__(self, name: str = 'Program Name', release: str = '0.0.0',
                 left_content: any = Text('', align=CENTER),
                 right_content: any = Text('', align=RIGHT),
                 widget_id: str = None):
        super().__init__(Padding(
            LineBox(AttrMap(Columns([
                left_content,
                AttrWrap(Text(f"{name} {release}", align=CENTER), 'header', 'header'),
                right_content
            ]), 'header')),
            align=CENTER, left=1, right=2), widget_id=widget_id)


class Footer(IdWidget):

    def __init__(self, left_content: any = Text('', align=LEFT),
                 right_content: any = Text('', align=RIGHT), widget_id: str = None):
        super().__init__(Padding(LineBox(AttrMap(Columns([
            left_content,
            right_content,
        ]), 'header')), align=CENTER, left=1, right=2), widget_id=widget_id)


class ListItem(IdWidget):

    def __init__(self, item_data: any, index: int = 0, formatter: any = None,
                 unselected: str = 'normal', selected: str = 'highlighted', keypress_callback: any = None,
                 widget_id: str = None):
        self.item_data = item_data
        self.item_data['index'] = index
        self.keypress_callback = keypress_callback

        label = "no label set"
        if type(item_data) == str:
            label = item_data
        elif formatter is not None:
            label = formatter(item_data)

        if type(label) == str:
            super().__init__(WidgetWrap(AttrWrap(Text(label), unselected, selected)), widget_id=widget_id)
        else:
            super().__init__(label, widget_id=widget_id)

    def selectable(self):
        return True

    def keypress(self, size, key):
        logging.info(f"{key} key pressed")
        if self.keypress_callback:
            self.keypress_callback(size, key, data=self.item_data)
        return key


class ListViewListBox(IdWidget):

    def __init__(self, body: any, double_click_callback: any = None, widget_id: str = None):
        self.double_click_callback = double_click_callback
        self.last_time_clicked = time.time()
        super().__init__(ScrollingListBox(body, with_scrollbar=UCMScrollBar), widget_id)

    def set_double_click_callback(self, double_click_callback: any = None):
        self.double_click_callback = double_click_callback
        return self

    def mouse_event(self, size, event, button, col, row, focus):
        logging.info(f"{event} {button} {size} {focus}")
        if event == 'mouse release':
            now = time.time()
            if self.last_time_clicked and (now - self.last_time_clicked < 0.5):
                logging.info(f"Triggering mouse double click event")
                if self.double_click_callback is not None:
                    self.double_click_callback()
            self.last_time_clicked = now
        else:
            return super().mouse_event(size, event, button, col, row, focus)


class ListView(IdWidget):

    def __init__(self, name: str, filter_fields: list = None, widget_id: str = None):
        self.name = name
        self.selected = None
        self.column_length = []
        self.filter_edit = None
        self.filter_columns = None
        self.filter_fields = [] if filter_fields is None else filter_fields
        register_signal(self.__class__, ['record_selected'])
        self.walker = SimpleFocusListWalker([])
        super().__init__(
            WidgetWrap(ListViewListBox(self.walker).set_double_click_callback(self.double_click_callback)),
            widget_id=widget_id)
        self.filter_and_set('')

    def modified(self):
        list_item, _i = self.walker.get_focus()
        if list_item is not None:
            emit_signal(self, 'record_selected', list_item)

    def record_selected(self, list_item: ListItem):
        logging.info(f"Record selected : {list_item} {list_item.item_data}")
        self.selected = list_item
        self.selected_callback(list_item)

    def double_click_callback(self):
        logging.debug(f'ListViewHandler[{self.name}] double_click_callback')

    def selected_callback(self, list_item: ListItem):
        logging.debug(f'ListViewHandler[{self.name}] {list_item.item_data} selected_callback')

    def _set_data(self, data: list = None):
        if data is None:
            data = []

        disconnect_signal(self.walker, 'modified', self.modified)
        disconnect_signal(self, 'record_selected', self.record_selected)
        self.walker.clear()

        self.walker.extend(
            [ListItem(
                item_data,
                index=idx,
                formatter=self.formatter,
                keypress_callback=self.keypress_callback)
                for idx, item_data in enumerate(data)])

        connect_signal(self.walker, "modified", self.modified)
        connect_signal(self, 'record_selected', self.record_selected)

        self.walker.set_focus(0)

    def get_header(self):
        return f'Data'

    def filters_clear(self):
        pass

    def formatter(self, record: any):
        return f'{record}'

    def filter_data(self, filter_string: str):
        # noinspection PyTypeChecker
        return list(filter(lambda k: filter_string.lower() in k.lower(), self.fetch_data))

    def filter_and_set(self, filter_string: str):
        self._set_data(self.filter_data(filter_string))

    def keypress_callback(self, size, key, item_data: any = None):
        logging.debug(f'ListViewHandler[{self.name}] {key} pressed')

    def _evaluate(self, filter_string: str, record: dict):
        for key in self.filter_fields:
            if key in record and filter_string.lower() in record[key].lower():
                return True
        return False

    def filter_data(self, filter_string: str):
        data = self.fetch_data()
        if filter_string is None or filter_string.strip() == '':
            return data
        return list(filter(lambda k: self._evaluate(filter_string, k), data))

    def filters_clear(self):
        self.filter_edit.edit_text = ""
        self.filter_columns.set_focus(1)

    def get_filter_widgets(self):
        self.filter_edit = Edit(align=LEFT)
        connect_signal(self.filter_edit, "change", self.filter_action, user_args=[])

        self.filter_columns = Columns([
            (15, AttrWrap(Text('Filter Text:  ', align=RIGHT), 'header', 'header')),
            (35, AttrWrap(self.filter_edit, 'filter', 'filter'))])
        return self.filter_columns

    def filter_action(self, _edit_widget, text_input):
        # noinspection PyProtectedMember
        self.filter_and_set(text_input)
        self.filter_columns.set_focus(1)


class View(IdWidget):
    def __init__(self, list_view: ListView, widget_id: str = None):
        self.list_view = list_view
        terminal_cols, terminal_rows = raw_display.Screen().get_cols_rows()
        list_rows = (terminal_rows - 11)  # header:3 + footer: 3 + border:2 + tableHeader: 1 + filter: 2 = 11

        if type(list_view.get_header()) == str:
            list_view.header_text_w = AttrWrap(Text(list_view.get_header()), 'header', 'header')
        else:
            list_view.header_text_w = list_view.get_header()

        master_pile = Pile([
            list_view.header_text_w,
            BoxAdapter(self.list_view, list_rows),
            Divider(u'\u2500'),
            self.list_view.get_filter_widgets(),
        ])
        super().__init__(Filler(master_pile, 'top'), widget_id=widget_id)


class HelpBody(IdWidget):

    heading_re = re.compile("^(#+)\s*(.*?)\s*$")

    bullet_re = re.compile("^(\s*)(\*)\s*(.*)$")

    palette = {'h': [
        None,
        AttrSpec('light green', 'default'),
        AttrSpec('light green', 'default'),
        AttrSpec('dark cyan', 'default'),
        AttrSpec('dark green', 'default'),
        AttrSpec('dark blue', 'default')
    ], 'normal': AttrSpec('light gray', 'default'), 'bullet': AttrSpec('light cyan', 'default'),
        'bold': AttrSpec('light cyan', 'default')}

    # noinspection PyPep8
    def __init__(self, widget_id: str = None):
        self.w_list = []

        for line in self.load():
            line = line.expandtabs(4)
            line_fmt = []

            header_match = self.heading_re.match(line.rstrip())
            bullet_match = self.bullet_re.match(line)

            if header_match:
                try:
                    line_fmt.append(
                        (self.palette['h'][len(header_match.group(1))], f"{header_match.group(2).replace('*','').replace('`','')}"))
                    self.w_list.append(Text(line_fmt))
                    continue
                except IndexError as _e:
                    logging.error(f'{header_match.group(1)}')
                    logging.error(f'{header_match.group(2)}')
                    pass
            elif bullet_match:
                line_fmt.append((self.palette['bullet'], u"\u25c6 %s" % (bullet_match.group(3))))
                self.w_list.append(Text(line_fmt))
                continue

            if not "```" in line:
                line_fmt.append((self.palette['normal'], line.rstrip()))
            else:
                for token in line.split("```"):
                    if "```%s```" % token in line:
                        line_fmt.append((self.palette['bold'], token))
                    elif len(token) > 0:
                        line_fmt.append((self.palette['normal'], token))
            self.w_list.append(Text(line_fmt))
        super().__init__(Pile([
            ScrollingListBox(SimpleListWalker(self.w_list),
                             with_scrollbar=UCMScrollBar)
        ]), widget_id=widget_id)

    def load(self):
        with (open(f'{os.path.dirname(__file__)}/help.txt', "r")) as f:
            return f.readlines()
        return []


# vim: ts=4 sw=4 et
