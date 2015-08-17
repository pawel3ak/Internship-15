# -*- coding: utf-8 -*-
"""
:created on: '13/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

import socket
import argparse
import multiprocessing as mltpr
from threading import Thread

import reservation_queue as queue
from checking_loop import checking_reservation_queue


HOST_IP = "127.0.0.1"
HOST_PORT = 5005
QUEUE_FILE_NAME = "reservation_queue"



def generate_password(passw_lenght = 4):
    import random

    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    password = ""
    for i in range(passw_lenght):
        next_sign = random.randrange(len(alphabet))
        password += alphabet[next_sign]
    return password


def response(connect, data):
    working_dictionary = {}
    try:
        message = working_dictionary[data]
    except Exception:
        message = 'Wrong command'
    connect.send(message)
    connect.close()


def new_request(queue_file_name, request):
    id = 1  #new ID number
    request['ID'] = id
    request['password'] = generate_password()
    queue.write_to_queue(queue_file_name, request)
    if queue.check_queue_length(queue_file_name) == 1:
        checking_reservation_queue(queue_file_name, False)
    return ("Add to reservation queue")


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

    # set up server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(5)

    thread = Thread(target=checking_reservation_queue, args=[queue_file_name])
    thread.daemon = True
    thread.start()

    while True:
        connect, address = sock.accept()
        data = connect.recv(1024).strip()
        if data == "KONIEC":
            break
        response(connect, data)

    sock.close()


if __name__ == "__main__":
    main_server()
