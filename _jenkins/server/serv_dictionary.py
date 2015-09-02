"""
:created on: '20/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

import json
import logging


logger = logging.getLogger("server." + __name__)


# update record in dictionary
def update_record(dictionary, server_id, reservation_id=None, busy_status=None,
                  time_add=None, duration=None, tl_name=None, job_test_status=None):
    if reservation_id is not None:
        dictionary[server_id]["reservationID"] = reservation_id
    if busy_status is not None:
        dictionary[server_id]["busy_status"] = busy_status
    if time_add is not None:
        dictionary[server_id]["time_add"] = time_add
    if duration is not None:
        dictionary[server_id]["duration"] = duration
    if tl_name is not None:
        dictionary[server_id]["tl_name"] = tl_name
    if job_test_status is not None:
        dictionary[server_id]["job_test_status "] = job_test_status


def get_first_not_busy(dictionary):
    for record in dictionary:
        if not dictionary[record]['busy_status']:
            return record
    return None


def get_not_busy_reservation_list(dictionary):
    record_list = []
    for record in dictionary:
        if not dictionary[record]['busy_status']:
            record_list.append(record)
            logger.debug("reservation {} - no busy".format(dictionary[record]['reservationID']))
        else:
            logger.debug("reservation {} - busy".format(dictionary[record]['reservationID']))
    return record_list


def get_busy_list(dictionary):
    record_list = []
    for record in dictionary:
        if dictionary[record]['busy_status']:
            record_list.append(record)
            logger.debug("reservation {} - busy".format(dictionary[record]['reservationID']))
        else:
            logger.debug("reservation {} - no busy".format(dictionary[record]['reservationID']))
    return record_list



def create_file(new_file):
    with open(new_file, "ab+") as open_file:
        open_file.close()


def write_dictionary_to_file(file_name, dictionary):
    with open(file_name, "wb") as open_file:
        json.dump(dictionary, open_file)


def get_dictionary_from_file(file_name):
    dictionary = {}
    temp_dictionary = {}
    with open(file_name, "rb") as open_file:
        if len(open_file.readlines()) > 0:
            open_file.seek(0, 0)
            temp_dictionary = json.load(open_file)
    for record in temp_dictionary:
        if temp_dictionary[record]['reservationID'] is not None:
            dictionary[int(record)] = temp_dictionary[record]
    return dictionary
