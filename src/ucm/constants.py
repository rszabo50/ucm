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

PROGRAM_NAME = 'ucm'
PROGRAM_TITLE = 'Urwid rendered Connection Manager'
PROGRAM_VERSION = '0.0.11'
SCM_URL = 'https://github.com/rszabo50/ucm'

MAIN_PALETTE = [
    ('header', 'dark cyan', 'default', "default", "dark cyan", "default"),
    ("normal", "dark cyan", "default"),
    ("highlighted", "light green", "default"),
    ("reverse-hl", "default", "dark cyan"),
    ("filter", 'default,underline', 'default', 'default,underline', 'default,underline', '#88a'),
    ('black', 'white', 'black'),
    ('dark red', 'white', 'dark red'),
    ('dark green', 'white', 'dark green'),
    ('brown', 'white', 'brown'),
    ('dark blue', 'white', 'dark blue'),
    ('dark magenta', 'white', 'dark magenta'),
    ('dark cyan', 'white', 'dark cyan'),
    ('light gray', 'black', 'light gray'),
    ('dark gray', 'white', 'dark gray'),
    ('light red', 'white', 'light red'),
    ('light green', 'white', 'light green'),
    ('yellow', 'black', 'yellow'),
    ('light blue', 'white', 'light blue'),
    ('light magenta', 'white', 'light magenta'),
    ('light cyan', 'black', 'light cyan'),
    ('white', 'black', 'white'),
    ('border', 'dark cyan', 'default'),
    ('shadow', 'default', 'light gray'),
    ('selectable', 'default', 'dark cyan'),
    ('focus', 'default', 'dark cyan', 'bold'),
    ('focustext', 'light gray', 'dark blue'),
    ('button normal', 'light gray', 'dark blue', 'standout'),
    ('button select', 'white', 'dark green')
]

# vim: ts=4 sw=4 et
