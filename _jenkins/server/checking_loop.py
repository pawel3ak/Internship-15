# -*- coding: utf-8 -*-
"""
:created on: '13/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

from time import sleep
from threading import Thread
import os

import reservation_queue as queue
import sdictionary
import supervisor
from tl_reservation import TestLineReservation


def get_catalog_list(dir):
    dirlist = []
    [dirlist.append(x) for x in os.listdir(dir) if os.path.isdir(os.path.join(dir,x))]
    return dirlist


def make_queue_from_test(queue_file, dir):
    dirlist = get_catalog_list(dir)
    for directory in dirlist:
        request = {'reservation_data':
                       {'testline_type' : 'CLOUD_F',
                        'duration': 120},
                   'serverID': queue.get_server_ID_number(),
                   'password': queue.generate_password(),
                   'user_info': None,
                   'jenkins_info': {'parameters': {'name': directory}}
                   }
        queue.write_to_queue(queue_file, request)


def start_reservation(queue_file, server_dictionary, handle_dictionary):
    request = queue.read_next_from_queue(queue_file)
    # queue.delete_reservation_from_queue(queue_file, request["serverID"], request["password"])
    thread = Thread(target=supervisor.main, args=[request["serverID"], request["reservation_data"], server_dictionary, request["user_info"], request["jenkins_info"]])
    thread.daemon = True
    thread.start()
    handle_dictionary[request["serverID"]] = thread


def checking_reservation_queue(queue_file_name, priority_queue_file_name, number_of_free_tl, server_dictionary, handle_dictionary, loop = True):
    test_reservation = TestLineReservation()
    while True:
        print "loop"
        checking_tl_busy(server_dictionary, handle_dictionary)
        print (test_reservation.get_available_tl_count_group_by_type())['CLOUD_F']
        print number_of_free_tl
        print queue.check_queue_length(queue_file_name)
        if ((test_reservation.get_available_tl_count_group_by_type())['CLOUD_F'] > number_of_free_tl):
            if queue.check_queue_length(priority_queue_file_name) > 0:
                start_reservation(priority_queue_file_name, server_dictionary, handle_dictionary)
            elif queue.check_queue_length(queue_file_name) > 0:
                start_reservation(queue_file_name, server_dictionary, handle_dictionary)
            elif queue.check_queue_length(queue_file_name) == 0:
                make_queue_from_test(queue_file_name, '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN')
                start_reservation(queue_file_name, server_dictionary, handle_dictionary)
            print "SCRIPT"
        if loop:
            sleep(30) # 1800??
        else:
            break

def checking_tl_busy(server_dictionary, handle_dictionary):
    """

    :type server_dictionary:
    :type handle_dictionary:
    """
    while True:
        no_busy_reservation = sdictionary.get_first_not_busy(server_dictionary)
        if no_busy_reservation is None:
            break
        reservation_tl_id = server_dictionary[no_busy_reservation]["reservation_id"]
        handle_dictionary[no_busy_reservation].join()
        tl_reservation = TestLineReservation(reservation_tl_id)
        tl_reservation.release_reservation()
        del handle_dictionary[no_busy_reservation]
        del server_dictionary[no_busy_reservation]



if __name__ == "__main__":
    directory = '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN'
    queue_file = 'reservation_queue'
    make_queue_from_test(queue_file, directory)
    print "END"
