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

from urwid import Frame, Button, Text, WidgetWrap, Divider, Pile, Padding, Filler, AttrWrap, LineBox, Columns, SolidFill, GridFlow, MainLoop, Overlay
from urwid import CENTER, MIDDLE
from ucm.Registry import Registry

import time


class DialogButton(Button):
    button_right = Text("")
    button_left = Text("")


# noinspection PyArgumentList
class DialogFrame(Frame):

    def keypress(self, size, key):
        if key == 'tab':
            if self.focus_part == 'body':
                self.set_focus('footer')
                return
            elif self.focus_part == 'footer':
                self.set_focus('body')
                return
        super().keypress(size, key)


class DialogDisplay(WidgetWrap):
    default_palette = [
        ('body', 'black', 'white'),
        ('border', 'black', 'white'),
        ('shadow', 'white', 'black'),
        ('selectable', 'black', 'dark cyan'),
        ('focus', 'black', 'dark cyan', 'bold'),
        ('focustext', 'light gray', 'dark blue'),
        ('button normal', 'light gray', 'dark blue', 'standout'),
        ('button select', 'white', 'dark green'),
    ]
    parent = None

    def __init__(self, text, width, height, body: any = None, loop: any = None, exit_cb: any = None,
                 palette: list = None):
        width = int(width) if width > 0 else ('relative', 80)
        height = int(height) if height > 0 else ('relative', 80)
        self.exit_cb = exit_cb
        self.buttons = []
        self.loop=loop
        self.palette = palette if palette is not None else self.default_palette

        if body is None:
            self.body = SolidFill(' ')
            fp = 'footer'
        else:
            self.body = body
            fp = 'body'

        self.frame = DialogFrame(self.body, focus_part=fp)
        if text is not None:
            self.frame.header = Pile([Text(text), Divider(u'\u2550')])
        w = self.frame

        # pad area around listbox
        w = Padding(w, ('fixed left', 2), ('fixed right', 2))
        w = Filler(w, ('fixed top', 1), ('fixed bottom', 1))
        w = AttrWrap(w, 'body')

        w = LineBox(w)

        # "shadow" effect
        w = Columns([w, ('fixed', 1, AttrWrap(
            Filler(Text(('border', ' ')), "top")
            , 'shadow'))])

        w = Frame(w, footer=AttrWrap(Text(('border', ' ')), 'shadow'))
        if self.loop is None:
            # this dialog is the main window
            # create outermost border area
            w = Padding(w, CENTER, width)
            w = Filler(w, MIDDLE, height)
            w = AttrWrap(w, 'border')
        else:
            # this dialog is a child window
            # overlay it over the parent window
            self.loop = loop
            self.parent = self.loop.widget
            w = Overlay(w, self.parent, CENTER, width + 2, MIDDLE, height + 2)
        self.view = w

        # Call WidgetWrap.__init__ to correctly initialize ourselves
        WidgetWrap.__init__(self, self.view)

    def add_buttons(self, buttons):
        button_list = []
        for name, exitcode in buttons:
            b = DialogButton(name, self.button_press)
            b.exitcode = exitcode
            b = AttrWrap(b, 'button normal', 'button select')
            button_list.append(b)
        self.buttons = GridFlow(button_list, 10, 3, 1, CENTER)
        self.frame.footer = Pile([Divider(u'\u2500'), self.buttons], focus_item=1)

    def button_press(self, button):
        if self.parent is not None:
            self.loop.widget = self.parent
        self.exit_cb(button)

    def show(self):
        if self.loop is None:
            self.loop = MainLoop(self.view, self.palette)
            exited = False
            while not exited:
                self.loop.run()
        else:
            self.loop.widget = self.view

# vim: ts=4 sw=4 et
