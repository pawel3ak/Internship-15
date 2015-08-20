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
import supervisor
from tl_reservation import TestLineReservation


def get_catalog_list(dir):
    dirlist = []
    [dirlist.append(x) for x in os.listdir(dir) if os.path.isdir(os.path.join(dir,x))]
    return dirlist


def make_queue_from_test(queue_file, dir):
    dirlist = get_catalog_list(dir)
    for directory in dirlist:
        request = {'reservation_data': {},
                   'serverID': queue.get_server_ID_number(),
                   'password': queue.generate_password(),
                   'user_info': {},
                   'jenkins_info': {'parameters': {'name': directory}}
                   }
        queue.write_to_queue(queue_file, request)


def start_reservation(queue_file):
    request = queue.read_next_from_queue(queue_file)
    queue.delete_reservation_from_queue(queue_file, request["serverID"], request["password"])
    thread = Thread(target=supervisor.main, args=[request["serverID"], request["reservation_data"], "000", request["user_info"], request["jenkins_info"]])
    thread.daemon = True
    thread.start()


def checking_reservation_queue(queue_file_name, priority_queue_file_name, number_of_free_tl, loop = True):
    test_reservation = TestLineReservation()
    while True:
        print "loop"
        if ((test_reservation.get_available_tl_count_group_by_type())['CLOUD_F'] > number_of_free_tl):
            if queue.check_queue_length(priority_queue_file_name) > 0:
                start_reservation(priority_queue_file_name)
            elif queue.check_queue_length(queue_file_name) > 0:
                start_reservation(queue_file_name)
            elif queue.check_queue_length(queue_file_name) == 0:
                make_queue_from_test(queue_file_name, '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN')
                start_reservation(queue_file_name)
            print "SCRIPT"
        if loop:
            sleep(30) # 1800??
        else:
            break
'''
def checking_tl_busy(tl_list):


'''

if __name__ == "__main__":
    directory = '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN'
    queue_file = 'reservation_queue'
    make_queue_from_test(queue_file, directory)
    print "END"
