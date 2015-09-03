# -*- coding: utf-8 -*-
"""
:created on: '17/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

import json
import logging
import os
import string

# create logger
logger = logging.getLogger("server." + __name__)


def write_to_queue_file(file_name, record):
    with open(file_name, "ab") as queue_file:
        json.dump(record, queue_file)
        queue_file.write("\n")


def read_next_reservation_record_from_queue(file_name):
    with open(file_name, "rb") as queue_file:
        return json.loads(queue_file.readline())


def delete_reservation_record_from_queue_file(file_name, queue_number, password):
    with open(file_name, "rb+") as queue_file:
        lines = queue_file.readlines()
        queue_file.seek(0)
        queue_file.truncate()
        for line in lines:
            if (json.loads(line)["serverID"] == queue_number) & (json.loads(line)["password"] != password):
                logger.warning("Wrong password")
                return -101
        logger.debug("Delete from queue serverID: %d", queue_number)
        for line in lines:
            if json.loads(line)["serverID"] != queue_number:
                queue_file.write(line)
    return 0


def check_queue_length(file_name):
    with open(file_name, "rb") as queue_file:
        return len(queue_file.readlines())
        # add option to ignor empty lines!!!!!!!!!!!!


def get_server_id_number():
    id_file = "files/temp_id"
    # check if id_file exists
    with open(id_file, "ab+") as opened_file:
        lines = opened_file.readlines()
        if len(lines) == 1:
            id_number = json.loads(lines[0]) + 1
        else:
            id_number = 1
        opened_file.seek(0)
        opened_file.truncate()
        json.dump(id_number, opened_file)
        return id_number


def generate_password(passw_lenght=4):
    import random
    alphabet = string.letters+string.digits
    ''.join(random.choice(alphabet) for _ in range(3))
    password = ""
    for i in range(passw_lenght):
        next_sign = random.randrange(len(alphabet))
        password += alphabet[next_sign]
    return password


if __name__ == "__main__":
    print get_server_id_number()
