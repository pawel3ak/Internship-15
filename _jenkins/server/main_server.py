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
from multiprocessing import Manager
import tl_reservation
import reservation_queue as queue
from checking_loop import main_checking_loop


HOST_IP = "127.0.0.1"
HOST_PORT = 5005
QUEUE_FILE_NAME = "reservation_queue"
PRIORITY_QUEUE_FILE_NAME = "reservation_prority_queue"
FREE_TL = 1
MAX_TL = 2


def response(connect, message, queue_file_name, priority_queue_file_name, server_dictionary):
    if message == "request/create_reservation":
        new_request(connect, queue_file_name, priority_queue_file_name, server_dictionary)
    elif message == "request/available_tl_count":
        _get_available_tl_count(connect)
    elif message == "request/get_info":
        _get_tests_info(connect, server_dictionary, specific = True)
    elif message == "request/get_all":
        _get_tests_info(connect, server_dictionary)
    else:
        connect.send("Wrong command")
        connect.close()

def _get_tests_info(connect, parent_dict, specific = None):
    connect.send("OK")
    string_to_send = str(parent_dict)
    if specific:
        data = connect.recv(1024).strip()
        string_to_send = str(parent_dict[int(data)])
    connect.send(string_to_send)
    connect.close()


def _get_available_tl_count(connect):
    testline_handle = tl_reservation.TestLineReservation()
    connect.send(str((testline_handle.get_available_tl_count_group_by_type())['CLOUD_F']))
    connect.close()


def new_request(connect, queue_file_name, priority_queue_file_name, server_dictionary):
    connect.send("OK")
    data = connect.recv(1024).strip()
    request = json.loads(data)
    request['serverID'] = queue.get_server_id_number()
    request['password'] = queue.generate_password()
    if request['priority'] == 0:
        request.pop('priority')
        queue.write_to_queue(queue_file_name, request)
    elif request['priority'] == 1:
        request.pop('priority')
        queue.write_to_queue(priority_queue_file_name, request)
    '''
    if (queue.check_queue_length(queue_file_name) == 1) or (queue.check_queue_length(priority_queue_file_name) == 1):
        checking_reservation_queue(queue_file_name, priority_queue_file_name, server_dictionary, False)
    '''
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
    max_testline = MAX_TL
    queue_file_name = args.file
    priority_queue_file_name = args.priority

    # create files if no exist
    queue.create_file(queue_file_name)
    queue.create_file(priority_queue_file_name)

    # create server and process dictionary
    man = Manager()
    server_dict = man.dict()
    server_dict = {}
    handle_dict = man.dict()
    handle_dict = {}
    server_dict[1] = {'cos' : 'innego',
                      'busy_status' : True}

    # set up server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(5)

    # start checking loop

    thread = Thread(target=main_checking_loop, args=[queue_file_name, priority_queue_file_name, free_testline, max_testline, server_dict, handle_dict])
    thread.daemon = True
    thread.start()

    # main server loop
    while True:
        connect, address = sock.accept()
        data = connect.recv(1024).strip()
        if data == "KONIEC":
            break
        response(connect, data, queue_file_name, priority_queue_file_name, server_dict)

    sock.close()


if __name__ == "__main__":
    main_server()
