#!/usr/bin/env python
#-*- encoding: utf-8 -*-
# debianitram (at) gmail.com



# First Read Lines
first_read_lines = 50

services = {
            'apache2': {'commands': ['restart', 'start', 'stop'],
                        'path_log': '/var/log/apache2/access.log',
                        },
            
            'log': {'commands': ['list_of_command'],
                    'path_log': '/home/debianitram/log.log'},

            'other': {'commands': ['list_of_command'],
                      'path_log': '/home/debianitram/other.log'}
        }
