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

# Created by rszabo50 at 2022-02-07


class Registry(dict):
    __instance = None

    def __new__(cls, *args):
        if cls.__instance is None:
            cls.__instance = dict.__new__(cls)
        return cls.__instance

    def set(self, k, v, overwrite=True):
        if overwrite or self.get(k) is None:
            setattr(self.__instance, k, v)

    def get(self, k):
        return getattr(self.__instance, k) if hasattr(self.__instance, k) else None


# vim: ts=4 sw=4 et
