# -*- coding: utf-8 -*-
"""
:created on: '13/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

from time import sleep

import reservation_queue as queue
from tl_reservation import TestLineReservation


def checking_reservation_queue(queue_file_name, loop = True):
    while True:
        print "loop"
        test_reservation = TestLineReservation()
        if (queue.check_queue_length(queue_file_name) > 0) & (test_reservation.get_available_tl_count() > 2):
            # start our script
            print "SCRIPT"
        if loop:
            sleep(10) # 1800??
        if loop is False:
            break
