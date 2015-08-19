# -*- coding: utf-8 -*-
"""
:created on: '17/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

import json


def create_file(file):
    with open(file, "ab+") as open_file:
        pass


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
        # add option to ignor empty lines


if __name__ == "__main__":
    default_file = "reservation_queue"
    a = ({'serverID': 111, 'tekst': 'simple', 'list': 'list', 'password': 'abcd'})
    b = ({'serverID': 112, 'tekst': 'simple2', 'list': 'list2', 'password': 'abcd'})
    print check_queue_length(default_file)
    write_to_queue(default_file, a)
    write_to_queue(default_file, b)
    print check_queue_length(default_file)
    print read_next_from_queue(default_file)
    delete_reservation_from_queue(default_file, 111, 'abcd')
    print check_queue_length(default_file)
    delete_reservation_from_queue(default_file, 112, 'abcd')
    print check_queue_length(default_file)
