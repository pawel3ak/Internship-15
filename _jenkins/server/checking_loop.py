# -*- coding: utf-8 -*-
"""
:created on: '13/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

from time import sleep
import json
from threading import Thread

import reservation_queue as queue
import supervisor
from tl_reservation import TestLineReservation


def checking_reservation_queue(queue_file_name, priority_queue_file_name, loop = True):
    while True:
        print "loop"
        test_reservation = TestLineReservation()
        if (test_reservation.get_available_tl_count() >= 2):
            if queue.check_queue_length(priority_queue_file_name) > 0:
                request = queue.read_next_from_queue(priority_queue_file_name)
                sleep(15)
                queue.delete_reservation_from_queue(priority_queue_file_name, request["serverID"], request["password"])
                thread = Thread(target=supervisor.main, args=[request["serverID"], request["reservation_data"], "parent ID", request["user_info"], request["jenkins_info"]])
                thread.daemon = True
                thread.start()
            elif queue.check_queue_length(queue_file_name) > 0:
                request = queue.read_next_from_queue(queue_file_name)
                sleep(15)
                queue.delete_reservation_from_queue(queue_file_name, request["serverID"], request["password"])
                thread = Thread(target=supervisor.main, args=[request["serverID"], request["reservation_data"], "parent ID", request["user_info"], request["jenkins_info"]])
                thread.daemon = True
                thread.start()
            print "SCRIPT"

        if loop:
            sleep(30) # 1800??
        if loop is False:
            break
