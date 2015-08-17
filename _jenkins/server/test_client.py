# -*- coding: utf-8 -*-
"""
:created on: '13/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

import socket
import sys

HOST_IP, HOST_PORT = "127.0.0.1", 5005

if sys.argv > 1:
        data = ""
        for message in sys.argv[1:]:
            pass
            data += str(message) + " "

sock = socket.socket(socket.AF_INET,
                     socket.SOCK_STREAM)
sock.connect((HOST_IP, HOST_PORT))
sock.send(data)
while True:
        response = sock.recv(1024)
        if response == "":
            break
        print response,

sock.close()


