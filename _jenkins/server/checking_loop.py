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
        request = {'reservation_data': {'testline_type': 'CLOUD_F',
                                        'duration': 120},
                   'serverID': queue.get_server_id_number(),
                   'password': queue.generate_password(),
                   'user_info': None,
                   'jenkins_info': {'parameters': {'name': directory}}
                   }
        queue.write_to_queue(queue_file, request)


def start_new_reservation(queue_file, server_dictionary, handle_dictionary):
    request = queue.read_next_from_queue(queue_file)
    queue.delete_reservation_from_queue(queue_file, request["serverID"], request["password"])
    thread = Thread(target=supervisor.main, args=[request["serverID"],
                                                  request["reservation_data"],
                                                  server_dictionary,
                                                  request["user_info"],
                                                  request["jenkins_info"]])
    thread.daemon = True
    thread.start()
    handle_dictionary[request["serverID"]] = thread


def end_reservation(server_id, server_dictionary, handle_dictionary):
    reservation_tl_id = server_dictionary[server_id]["reservation_id"]
    handle_dictionary[server_id].join()
    tl_reservation = TestLineReservation(reservation_tl_id)
    tl_reservation.release_reservation()
    del handle_dictionary[server_id]
    del server_dictionary[server_id]


def checking_reservation_queue(queue_file_name, priority_queue_file_name, number_of_free_tl, max_tl_number,
                               server_dictionary, handle_dictionary, loop = True):
    test_reservation = TestLineReservation()
    while True:
        print "reservation loop"
        print (test_reservation.get_available_tl_count_group_by_type())['CLOUD_F']
        print number_of_free_tl
        print queue.check_queue_length(queue_file_name)
        if ((test_reservation.get_available_tl_count_group_by_type())['CLOUD_F'] > number_of_free_tl) & \
                (len(server_dictionary)<max_tl_number):
            if queue.check_queue_length(priority_queue_file_name) > 0:
                start_new_reservation(priority_queue_file_name, server_dictionary, handle_dictionary)
            elif queue.check_queue_length(queue_file_name) > 0:
                start_new_reservation(queue_file_name, server_dictionary, handle_dictionary)
            elif queue.check_queue_length(queue_file_name) == 0:
                make_queue_from_test(queue_file_name, '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN')
                start_new_reservation(queue_file_name, server_dictionary, handle_dictionary)
            print "SCRIPT"
            sleep(3)
        else:
            break
        if loop is False:
            break


def checking_tl_busy(server_dictionary, handle_dictionary):
    for record in server_dictionary:
        if server_dictionary[record]['busy_status'] == True:
            # busy
            pass
        elif server_dictionary[record]['busy_status'] == False:
            # no busy
            end_reservation(server_dictionary[record]["server_id"], server_dictionary, handle_dictionary)



def main_checking_loop(queue_file_name, priority_queue_file_name, number_of_free_tl, max_tl_number,
                       server_dictionary, handle_dictionary):
    while True:
        print "main loop"
        checking_tl_busy(server_dictionary, handle_dictionary)
        checking_reservation_queue(queue_file_name, priority_queue_file_name, number_of_free_tl, max_tl_number,
                       server_dictionary, handle_dictionary, False)
        sleep(30)


if __name__ == "__main__":
    directory = '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN'
    queue_file = 'reservation_queue'
    make_queue_from_test(queue_file, directory)
    print "END"
