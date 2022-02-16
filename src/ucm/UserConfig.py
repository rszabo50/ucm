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

# Created by rszabo50 at 2022-02-09

from pathlib import Path
import os
import traceback
import yaml
import getpass
import subprocess
from shutil import which


class UserConfig(dict):
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

    def initialize(self):
        self.set('config_folder', f"{Path.home()}/.ucm", overwrite=False)
        self.set('ssh_config_file', f"{Path.home()}/.ucm/ssh_connections.yml", overwrite=False)
        setattr(self, 'docker', which('docker'))
        setattr(self, 'swarm_host', UserConfig.is_swarm_host())
        self.build_dot_ucm()
        self.load_ssh_config()

    def load_ssh_config(self):
        self.set('ssh_connections', UserConfig.load_yaml(self.get("ssh_config_file"), must_exist=True))

    @staticmethod
    def is_swarm_host():
        result = subprocess.check_output(['docker', 'info', '--format', '{{.Swarm.ControlAvailable}}'], stderr=subprocess.STDOUT)
        return result.splitlines()[0].decode("utf-8").strip().lower() == 'true'

    def build_dot_ucm(self):
        if not os.path.exists(self.get('config_folder')):
            os.makedirs(self.get('config_folder'))
        if not os.path.exists(self.get('ssh_config_file')):
            with open(self.get('ssh_config_file'), 'w') as f:
                f.write('\n'.join([
                    "# Each ssh connection is defined as:",
                    "# - name: hostname or identifier",
                    "#   address: ip or dns resolvable name",
                    "#   user: username to connect with",
                    "#   port: tcp port to use: default: 22",
                    "#   identity_file: <identity file to use if needed and its not your default key>",
                    "#   options: <any other ssh options, supported by the command line",
                    "#   category: <identifier ; makes filtering easier>",
                    "# Note: Because UCM will use the address variable to connect, common options like the identity file, port etc",
                    "#       can be done via your ~/.ssh/config e.g.",
                    "#         Host: 192.168.0.*",
                    "#             GSSAPIAuthentication no",
                    "#             StrictHostKeyChecking no",
                    "#             UserKnownHostsFile /dev/null",
                    "#             IdentityFile ~/.ssh/MyIdentifyFile.pem",
                    "",
                    " - name: localhost",
                    "   address: 127.0.0.1",
                    f"   user: {getpass.getuser()}",
                    "   category: sample",
                    ""
                ]))

    @staticmethod
    def load_yaml(filename: str, must_exist: bool = False):
        if os.path.exists(filename):
            with open(filename, "r") as stream:
                try:
                    return yaml.load(stream, Loader=yaml.SafeLoader)
                except yaml.YAMLError as _e:
                    traceback.print_exc()
                    raise RuntimeError(f"Unable to load {filename}.")
        else:
            if must_exist:
                raise RuntimeError(f"Unable to load {filename}. NOT FOUND")


UserConfig().initialize()

# vim: ts=4 sw=4 et
