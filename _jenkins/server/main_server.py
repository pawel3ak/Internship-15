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
import logging
import logging.handlers
from threading import Thread
from multiprocessing import Manager
import tl_reservation
import sdictionary
import reservation_queue as queue
from checking_loop import main_checking_loop


HOST_IP = "127.0.0.1"
HOST_PORT = 5005
QUEUE_FILE_NAME = "reservation_queue"
PRIORITY_QUEUE_FILE_NAME = "reservation_prority_queue"
SERVER_DICTIONARY_FILE_NAME = "server_dictionary_file"
FREE_TL = 1
MAX_TL = 3
MIN_TIME_TO_END = 1
MAX_RESERVATION_TIME = 2
EXTEND_TIME = 2


# create logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s %(levelname)8s: %(name)8s - %(filename)18s - %(funcName)15s: %(message)s')
# create file handler to file with logs
file_handler = logging.handlers.TimedRotatingFileHandler(filename='logs/server.log',
                                                         when='midnight',
                                                         interval=1,
                                                         backupCount=30)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
# add handler to the logger
logger.addHandler(file_handler)


def response(connect, message, queue_file_name, priority_queue_file_name, server_dictionary):
    if message == "request/create_reservation":
        new_request(connect, queue_file_name, priority_queue_file_name, server_dictionary)
    elif message == "request/available_tl_count":
        _get_available_tl_count(connect)
    elif message == "request/get_info":
        _get_tests_info(connect, server_dictionary, _specific=True)

    elif message == "request/get_all":
        _get_tests_info(connect, server_dictionary)
    else:
        connect.send("Wrong command")
        connect.close()


def _get_tests_info(connect, parent_dict, _specific=None):
    connect.send("OK")
    string_to_send = str(parent_dict)
    if _specific:
        data = connect.recv(1024).strip()
        try:
            string_to_send = str(parent_dict[int(data)])
        except:
            string_to_send = "No information about requested serverID"
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

    # create files if not exist
    logger.debug("Create servers files")
    queue.create_file(queue_file_name)
    queue.create_file(priority_queue_file_name)

    # create server and process dictionary
    logger.debug("Create servers dictionaries")
    man = Manager()
    server_dict = man.dict()
    server_dict = {}
    handle_dict = man.dict()
    handle_dict = {}

    # create file for server dictionary if not exist and read if exist
    sdictionary.create_file(SERVER_DICTIONARY_FILE_NAME)
    server_dict = sdictionary.get_dictionary_from_file(SERVER_DICTIONARY_FILE_NAME)


    # set up server
    logger.debug("Set up server")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(5)

    # start checking loop
    logger.info("Start new thread with checking loop")
    thread = Thread(target=main_checking_loop, args=[queue_file_name, priority_queue_file_name, SERVER_DICTIONARY_FILE_NAME,
                                                     free_testline, max_testline, server_dict, handle_dict, MIN_TIME_TO_END,
                                                     MAX_RESERVATION_TIME, EXTEND_TIME])
    thread.daemon = True
    thread.start()

    # main server loop
    logger.info("Start server loop - waiting for request")
    while True:
        connect, address = sock.accept()
        data = connect.recv(1024).strip()
        logger.debug("New request")
        if data == "KONIEC":
            break
        response(connect, data, queue_file_name, priority_queue_file_name, server_dict)

    sock.close()


if __name__ == "__main__":
    main_server()
