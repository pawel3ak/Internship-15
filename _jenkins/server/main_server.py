# -*- coding: utf-8 -*-
"""
:created on: '13/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

import socket
import argparse
import reservation_queue as queue
from tl_reservation import TestLineReservation
from time import sleep
from thread import *


HOST_IP = "127.0.0.1"
HOST_PORT = 5005
QUEUE_FILE_NAME = "reservation_queue"


def first():
    return "1 aaaa"


def second():
    return "2 bbbb"


def response(connect, data):
    working_dictionary = {'first': first(), 'second': second()}
    try:
        message = working_dictionary[data]
    except:
        message = 'Wrong command'
    sleep(5)
    connect.send(message)
    connect.close()


def check_reservation_queue(queue_file_name, loop = True):
    while loop:
        test_reservation = TestLineReservation()
        if (queue.check_queue(queue_file_name) > 0) & (test_reservation.get_available_tl_count() > 2):
            # start our script
            print "SCRIPT"
        if loop:
            sleep(60) # 1800??


def new_request(queue_file_name, request):
    if queue.check_queue(queue_file_name) > 0:
        queue.write_to_queue(queue_file_name, request)
        print("Add to reservatuon queue")


def main_server():
    parser = argparse.ArgumentParser(argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-a', '--host', default=HOST_IP,
                        help='set IP addres for server')
    parser.add_argument('-p', '--port', type=int, default=HOST_PORT,
                        help='set port number for server')
    parser.add_argument('-f', '--file', default=QUEUE_FILE_NAME,
                        help='set file for reservation queue')

    args = parser.parse_args()
    host = args.host
    port = args.port
    queue_file_name = args.file

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
