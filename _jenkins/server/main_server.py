# -*- coding: utf-8 -*-
"""
:created on: '13/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

import socket
import argparse
from time import sleep
from thread import *


HOST_IP = "127.0.0.1"
HOST_PORT = 5005


def first():
    return "1 aaaa"


def second():
    return "2 bbbb"


def response(connect, data):
    working_dictionary = {'pierwszy': pierwszy(), 'drugi': drugi()}
    try:
        message = working_dictionary[data]
    except:
        message = 'Wrong command'
    sleep(5)
    connect.send(message)
    connect.close()


def main_server():
    parser = argparse.ArgumentParser(argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-a', '--host', default=HOST_IP,
                        help='set IP addres for server')
    parser.add_argument('-p', '--port', type=int, default=HOST_PORT,
                        help='set port number for server')

    args = parser.parse_args()
    host = args.host
    port = args.port

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(1)

    while True:
        connect, address = sock.accept()
        data = connect.recv(1024).strip()
        if data == "KONIEC":
            break
        response(connect, data)


if __name__ == "__main__":
    main_server()
