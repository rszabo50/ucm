#!/usr/bin/env python3

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

# Created by szabor at 2022-03-17

import logging
from collections import OrderedDict

from urwid import AttrWrap, Button, Edit, RadioButton, Text


class TabGroupFocus:
    def __init__(self):
        self.frame = None
        self.frame_pos = None
        self.pile = None
        self.pile_pos = 0
        self.container = None
        self.container_pos = -1

    def __str__(self):
        return f"TabGroupFocus({self.frame}:{self.frame_pos} {self.container}:{self.container_pos})"


class TabGroupNode:
    def __init__(self):
        self.current = None
        self.next = None

    def set_current(self, frame, frame_pos, container, container_pos, pile=None, pile_pos=-1):
        self.current = TabGroupFocus()
        self.current.frame = frame
        self.current.frame_pos = frame_pos
        self.current.container = container
        self.current.container_pos = container_pos
        self.current.pile = pile
        self.current.pile_pos = pile_pos
        return self

    def focus_next(self):
        if self.next.frame is not None and self.next.frame_pos is not None:
            logging.info("moving to frame")
            self.next.frame.focus_position = self.next.frame_pos
        else:
            logging.error("frame ref is not good")

        if self.next.pile is not None and self.next.pile_pos >= 0:
            self.next.pile.focus_position = self.next.pile_pos

        if self.next.container is not None and self.next.container_pos >= 0:
            if hasattr(self.next.container, "set_focus"):
                logging.info("moving to next container position")
                self.next.container.set_focus(self.next.container_pos)
            elif hasattr(self.next.container, "walker"):
                logging.info("moving to walker")
                self.next.container.walker.set_focus(self.next.container_pos)
            else:
                logging.error(f"{self.next.container} no handling enabled")
        else:
            logging.error("container ref is not good")


class TabGroupButton(Button, TabGroupNode):
    button_right = Text("")
    button_left = Text("")

    def keypress(self, size, key):
        logging.debug(f"TabGroupButton.keypress({size},{key}")
        if key == "tab":
            super().focus_next()
        super().keypress(size, key)


class TabGroupRadioButton(RadioButton, TabGroupNode):
    def keypress(self, size, key):
        logging.debug(f"TabGroupRadioButton.keypress({size},{key})")
        if key == "tab":
            super().focus_next()
        super().keypress(size, key)


class TabGroupEdit(Edit, TabGroupNode):
    def keypress(self, size, key):
        logging.debug(f"TabGroupEdit.keypress({size},{key}")
        if key == "tab":
            super().focus_next()
        super().keypress(size, key)


class TabGroupManager:
    def __init__(self):
        self.groups = OrderedDict()

    def add(self, name, frame, frame_position, base_widget, pile=None, pile_pos=-1):
        if hasattr(base_widget, "contents"):
            nodes = []
            for idx, item in enumerate(base_widget.contents):
                w = item[0].original_widget if isinstance(item[0], AttrWrap) else item[0]
                if hasattr(w, "set_current"):
                    w.set_current(frame, frame_position, base_widget, idx, pile=pile, pile_pos=pile_pos)
                    nodes.append(w)
            self.groups[name] = nodes
            self.relink()
        else:
            logging.debug(f" TYPE: {type(base_widget)}")
            if hasattr(base_widget, "set_current"):
                base_widget.set_current(frame, frame_position, base_widget, 0, pile=pile, pile_pos=pile_pos)
                self.groups[name] = [base_widget]
                self.relink()

    # noinspection PyBroadException
    def relink(self):
        nodes = []
        for arr in self.groups.values():
            nodes.extend(arr)
        for idx, node in enumerate(nodes):
            try:
                nodes[idx].next = nodes[idx + 1].current
            except:
                pass
        nodes[-1].next = nodes[0].current


# vim: ts=4 sw=4 et
