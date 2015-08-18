# -*- coding: utf-8 -*-
"""
:created on: '13/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

import socket
import sys
import json

HOST_IP, HOST_PORT = "127.0.0.1", 5005
request = "request/create_reservation"
data = json.dumps({'reservation_data' :
                       {'testline_type' : 'CLOUD_F'},
                   'user_info' :
                       {'first_name'    : 'Pawel',
                        'last_name'     : 'Nogiec',
                        'e-mail'        : 'pawel.nogiec@nokia.com'},
                   'jenkins_info' :
                       {'name' : 'test_job_tl_99',
                        'parameters' :
                            {'f_name'   : 'pierwszy',
                             't1'       : 'drugi',
                             't2'       : 'trzeci'}
                       },
                   })


sock = socket.socket(socket.AF_INET,
                     socket.SOCK_STREAM)
sock.connect((HOST_IP, HOST_PORT))
sock.send(request)
while True:
        response = sock.recv(1024)
        if response == 'OK':
            sock.send(data)
        elif response == "":
            break
        print response,
sock.close()


