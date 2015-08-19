# -*- coding: utf-8 -*-
"""
:created on: '13/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

import socket
import json
import argparse
from threading import Thread
import tl_reservation
import reservation_queue as queue
from checking_loop import checking_reservation_queue


HOST_IP = "127.0.0.1"
HOST_PORT = 5005
QUEUE_FILE_NAME = "reservation_queue"
PRIORITY_QUEUE_FILE_NAME = "reservation_prority_queue"
ID_NUMBER = 1
FREE_TL = 3


def generate_password(passw_lenght=4):
    import random

    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    password = ""
    for i in range(passw_lenght):
        next_sign = random.randrange(len(alphabet))
        password += alphabet[next_sign]
    return password


def response(connect, message, queue_file_name, priority_queue_file_name):
    if message == "request/create_reservation": new_request(connect, queue_file_name, priority_queue_file_name)
    elif message == "request/available_tl_count": _get_available_tl_count(connect)
    else:
        connect.send("Wrong command")
        connect.close()


def _get_available_tl_count(connect):
    testline_handle = tl_reservation.TestLineReservation()
    connect.send(str((testline_handle.get_available_tl_count_group_by_type())['CLOUD_F']))
    connect.close()


def new_request(connect, queue_file_name, priority_queue_file_name):
    connect.send("OK")
    data = connect.recv(1024).strip()
    request = json.loads(data)
    global ID_NUMBER
    request['serverID'] = ID_NUMBER
    ID_NUMBER += 1
    request['password'] = generate_password()
    if request['priority'] == 0:
        request.pop('priority')
        queue.write_to_queue(queue_file_name, request)
    elif request['priority'] == 1:
        request.pop('priority')
        queue.write_to_queue(priority_queue_file_name, request)
    if (queue.check_queue_length(queue_file_name) == 1) or (queue.check_queue_length(priority_queue_file_name) == 1):
        checking_reservation_queue(queue_file_name, priority_queue_file_name, False)
    connect.close()


def main_server():
    parser = argparse.ArgumentParser(argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-a', '--host', default=HOST_IP,
                        help='set IP addres for server')
    parser.add_argument('-p', '--port', type=int, default=HOST_PORT,
                        help='set port number for server')
    parser.add_argument('-t', '--freetl', type=int, default=FREE_TL,
                        help='set how many free telstline will be available for users')
    parser.add_argument('-f', '--file', default=QUEUE_FILE_NAME,
                        help='set file for reservation queue')
    parser.add_argument('-r', '--priority', default=PRIORITY_QUEUE_FILE_NAME,
                        help='set file for reservation priority queue')

    args = parser.parse_args()
    host = args.host
    port = args.port
    free_testline = args.freetl
    queue_file_name = args.file
    priority_queue_file_name = args.priority

    # create files if no exist
    queue.create_file(queue_file_name)
    queue.create_file(priority_queue_file_name)

    # set up server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(5)

    # start checking loop

    thread = Thread(target=checking_reservation_queue, args=[queue_file_name, priority_queue_file_name, free_testline])
    thread.daemon = True
    thread.start()

    # main server loop
    while True:
        connect, address = sock.accept()
        data = connect.recv(1024).strip()
        if data == "KONIEC":
            break
        response(connect, data, queue_file_name, priority_queue_file_name)

    sock.close()


if __name__ == "__main__":
    main_server()
