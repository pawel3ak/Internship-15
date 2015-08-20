# -*- coding: utf-8 -*-
"""
:created on: '17/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

import json


def create_file(new_file):
    with open(new_file, "ab+") as open_file:
        open_file.close()


def write_to_queue(file_name, record):
    with open(file_name, "ab") as queue_file:
        json.dump(record, queue_file)
        queue_file.write("\n")


def read_next_from_queue(file_name):
    with open(file_name, "rb") as queue_file:
        return json.loads(queue_file.readline())


def delete_reservation_from_queue(file_name, queue_number, password):
    with open(file_name, "rb") as queue_file:
        lines = queue_file.readlines()
    for line in lines:
        if (json.loads(line)["serverID"] == queue_number) & (json.loads(line)["password"] != password):
            print 'Wrong password'
            return -101
    with open(file_name, "wb") as queue_file:
        for line in lines:
            if json.loads(line)["serverID"] != queue_number:
                queue_file.write(line)
    return 0


def check_queue_length(file_name):
    with open(file_name, "rb") as queue_file:
        return len(queue_file.readlines())
        # add option to ignor empty lines!!!!!!!!!!!!


def get_server_id_number():
    id_file = "temp_id"
    with open(id_file, "ab+") as open_file:
        lines = open_file.readlines()
    if len(lines) == 0:
        write_to_queue(id_file, 1)
        return 1
    elif len(lines) == 1:
        id_number = read_next_from_queue(id_file) + 1
        with open(id_file, "wb+") as open_file:
            json.dump(id_number, open_file)
        return id_number
    else:
        id_number = 1
        with open(id_file, "wb+") as open_file:
            json.dump(id_number, open_file)
        return id_number


def generate_password(passw_lenght=4):
    import random
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    password = ""
    for i in range(passw_lenght):
        next_sign = random.randrange(len(alphabet))
        password += alphabet[next_sign]
    return password


if __name__ == "__main__":
    print get_server_id_number()
