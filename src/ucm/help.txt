# **U**rwid rendered **C**onnection **M**anager (**ucm**)


Released under GNU GPLv3.

https://www.gnu.org/licenses/gpl-3.0.en.html

This software can be used by anyone at no cost, however, if you like using this software and can support 

- please donate to any of your local charities (childrens hospitals, food banks, shelters, spca,  etc).

This program is free software: you can redistribute it and/or modify it under the terms of the 
GNU General Public License as published by the Free Software Foundation: GNU GPLv3. 
You must include this entire text with your distribution.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even 
the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
See the GNU General Public License for more details.

## About ucm

ucm is modeled after nccm (NCurses ssh Connection Manager), but built using urwid which provides a similar interface with
added mouse support. see: https://github.com/flyingrhinonz/nccm for details.

### UCM provides:

* a simple TUI for managing and connecting to ssh endpoints
* a simple TUI for attaching to Docker Containers that are present on your system

### UCM intended users

* You have dozens or more of hosts to manage via ssh.
* Your ssh requirements (identities, ports, users etc) differ from host to host, and you want to simplify things 
* You want a simple interfaces to get console access to your docker containers
* You want View all your hosts/containers at once and filter easily so that you know who to connect to.
* Have a need to use command line, don't have a GUI, or simply prefer to work more efficiently?

## UCM Configuration

Personal configurations are stored in ~/.ucm where 

config.yml:  is used to information about common runtime items:
    logfile - location of the log file
    loglevel - log level can be one of: debug, info, warning, error, critical

ssh_connnections.yml - used to provide a list of all your managed connections

```
    # Each ssh connection is defined as:
    # - name: hostname or identifier
    #   address: ip or dns resolvable name
    #   user: username to connect with
    #   port: tcp port to use: default: 22
    #   identity_file: identity file to use if needed and its not your default key
    #   options: any other ssh options#   
    #   category: identifier    
    #
    # Note: Because UCM will use the address variable to connect, common options like the identity file, port etc
    #       can be done via your ~/.ssh/config e.g.
    #         Host: 192.168.0.*
    #             GSSAPIAuthentication no
    #             StrictHostKeyChecking no
    #             UserKnownHostsFile /dev/null
    #             IdentityFile  ~/.ssh/MyIdentifyFile.pem

- name: test
  address: 192.168.0.4
  user: root
  port: 22
  options: -X

```

## UCM UI Controls

The UI controls are quite simple, The main interactions can all be done via the mouse. 

* Clicking on buttons, RadioButtons etc all work as you would expect via the mouse
* Clicking on a list will mark the row selected, and double clicking will trigger the connect action.


If your not using the mouse to control things:

* page-up, page-down will move up/down a page in the list views, and the help screen
* up/down arrows will scroll up/down one row at a time in the list views, and the help screen
