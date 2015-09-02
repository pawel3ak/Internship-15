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
import os
import logging
import logging.handlers
from threading import Thread
from multiprocessing import Manager
from time import sleep
import tl_reservation
import serv_dictionary
import reservation_queue as queue
from checking_loop import main_checking_loop
from utilities.logger_config import config_logger


HOST_IP = "127.0.0.1"
HOST_PORT = 5005
FILE_DIRECTORY = "files"
QUEUE_FILE_NAME = "reservation_queue"
SERVER_DICTIONARY_FILE_NAME = "server_dictionary_file"
FREE_TL = 1     # free tl number for users reservations
MAX_TL = 1      # max tl number which server can reserve
# time in hour
MIN_TIME_TO_END = 1     # min time when we can make a new task on tl
START_RESERVATION_TIME = 2  # reservation duration time
MAX_RESERVATION_TIME = 12   # max reservation duration time with extending
EXTEND_TIME = 2     # extend time


# create logger
logger = logging.getLogger("server")
config_logger(logger)


def response(connect, message, queue_file_name, server_dictionary):
    if message == "request/create_reservation":
        new_request(connect, queue_file_name)
    elif message == "request/available_tl_count":
        _get_available_tl_count(connect)
    elif message == "request/get_info":
        _get_tests_info(connect, server_dictionary, _specific=True)
    elif message == "request/get_all":
        _get_tests_info(connect, server_dictionary)
    else:
        logger.debug("Wrong command from client - send response and close connection")
        connect.send("Wrong command")
        connect.close()


def _get_tests_info(connect, parent_dict, _specific=None):
    connect.send("OK")
    string_to_send = str(parent_dict)
    if _specific:
        logger.debug("Get data from client")
        data = connect.recv(1024).strip()
        try:
            string_to_send = str(parent_dict[int(data)])
        except:
            string_to_send = "No information about requested serverID"
            logger.debug("Wrong server ID from client")
    logger.debug("Send response and close connection")
    connect.send(string_to_send)
    connect.close()


def _get_available_tl_count(connect):
    testline_handle = tl_reservation.TestLineReservation()
    logger.debug("Send response and close connection")
    connect.send(str((testline_handle.get_available_tl_count_group_by_type())['CLOUD_F']))
    connect.close()


def new_request(connect, queue_file_name):
    connect.send("OK")
    logger.debug("Get data from client")
    data = connect.recv(1024).strip()
    request = json.loads(data)
    request['serverID'] = queue.get_server_id_number()
    request['password'] = queue.generate_password()
    logger.debug("Save client request to queue")
    queue.write_to_queue(queue_file_name, request)
    logger.debug("Close connection")
    connect.close()


def main_server():
    logger.info("Start server configuration")
    logger.debug("Parsing arguments")
    parser = argparse.ArgumentParser(argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-a', '--host', default=HOST_IP,
                        help='set IP addres for server')
    parser.add_argument('-p', '--port', type=int, default=HOST_PORT,
                        help='set port number for server')
    parser.add_argument('-t', '--freetl', type=int, default=FREE_TL,
                        help='set how many free telstline will be available for users')
    parser.add_argument('-f', '--file', default=QUEUE_FILE_NAME,
                        help='set file for reservation queue')

    args = parser.parse_args()
    host = args.host
    port = args.port
    free_testline = args.freetl
    max_testline = MAX_TL
    queue_file_name = FILE_DIRECTORY + "/" + args.file
    server_dictionary_file_name = FILE_DIRECTORY + "/" + SERVER_DICTIONARY_FILE_NAME

    # create server and process dictionary
    logger.debug("Create servers dictionaries")
    man = Manager()
    server_dict = man.dict()
    server_dict = {}
    handle_dict = man.dict()
    handle_dict = {}

    # create files and directories if not exist
    logger.debug("Checking if necessary directories and files exist")
    # files directory
    if not os.path.isdir(FILE_DIRECTORY):
        logger.debug("Create %s directory", FILE_DIRECTORY)
        os.makedirs(FILE_DIRECTORY)
    # queue file
    if not os.path.exists(queue_file_name):
        logger.debug("Crate file: %s", queue_file_name)
        queue.create_file(queue_file_name)
    if not os.path.exists(server_dictionary_file_name):
        logger.debug("Crate file: %s", server_dictionary_file_name)
        serv_dictionary.create_file(server_dictionary_file_name)
    else:
        logger.debug("Load server dictionary from file: %s", server_dictionary_file_name)
        server_dict = serv_dictionary.get_dictionary_from_file(server_dictionary_file_name)

    # set up server
    logger.debug("Set up server config")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(5)

    # start checking loop
    logger.info("Start new thread with checking loop")
    thread = Thread(target=main_checking_loop, args=[queue_file_name, server_dictionary_file_name,
                                                     free_testline, max_testline, server_dict, handle_dict, MIN_TIME_TO_END,
                                                     START_RESERVATION_TIME, MAX_RESERVATION_TIME, EXTEND_TIME])
    thread.daemon = True
    thread.start()
    sleep(20)
    # main server loop
    logger.info("Start server loop - waiting for request")
    while True:
        connect, address = sock.accept()
        data = connect.recv(1024).strip()
        logger.debug("New request: %s", data)
        if data == "KONIEC":
            break
        response(connect, data, queue_file_name, server_dict)

    sock.close()
    logger.info("Server stopped")


if __name__ == "__main__":
    main_server()
