# -*- coding: utf-8 -*-
"""
:created on: '11/08/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nokia.com
"""

from supervisor_api import Supervisor, logger
from messages_logger import EXCEPTIONS_INFO
import time

def main(serverID, reservation_data, parent_dict, jenkins_info, user_info = None, TLreservationID = None):
    supervisor = Supervisor(serverID, reservation_data, parent_dict, jenkins_info, user_info = user_info, TLreservationID = TLreservationID)

    if supervisor.TLreservationID == None:
        supervisor.TLreservationID = supervisor.create_reservation(
            testline_type=reservation_data['testline_type'],
            # reservation_data['enb_build'],
            # reservation_data['ute_build'],
            # reservation_data['sysimage_build'],
            # reservation_data['robotle_revision'],
            # reservation_data['state'],
            duration=reservation_data['duration'])

    print supervisor.TLreservationID
    time.sleep(2)
    supervisor.get_TLreservationID()

    supervisor.set_parent_dict(busy_status=True)
    supervisor.reservation_status()
    supervisor.set_TLname(supervisor.get_TLname_from_ID())
    supervisor.set_TLaddress(supervisor.get_TLaddress_from_ID())

    #############################################################################
    #temporary hard-coded  variables:
    print supervisor.set_TLname('tl99_test')
    print supervisor.set_TLaddress('wmp-tl99.lab0.krk-lab.nsn-rdnet.net')
    print supervisor.set_user_info('Pawel','Nogiec','pawel.nogiec@nokia.com')
    ##############################################################################

    supervisor.set_parent_dict(busy_status=True)

    supervisor.set_job_api()
    if not supervisor.get_is_queue_or_running():
        supervisor.create_and_build_job()

    supervisor.get_jenkins_console_output()
    print supervisor.get_job_status()

    job_tests_parsed_status = supervisor.get_job_tests_status()
    supervisor.set_parent_dict(busy_status=True, job_tests_parsed_status=job_tests_parsed_status)

    print supervisor.ending()
    print job_tests_parsed_status

    if supervisor.has_got_fail :
        supervisor.remove_tag_from_file()

    supervisor.send_information()

    supervisor.set_parent_dict(busy_status=False, job_tests_parsed_status=job_tests_parsed_status)
    return 0

'''
if __name__ == '__main__':
    import os
    from threading import Thread
    dir_list = []
    path = '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/'
    [dir_list.append(dir) for dir in os.listdir(path) if os.path.isdir(os.path.join(path,dir))]

    """ ['LTE1819', 'LTE2351', 'LTE738', 'LTE1841', 'LTE2465', 'CRT', 'LTE1899', 'LTE2209',
    'LBT1558', 'LTE1905', 'LTE1879', 'LTEXYZ-new', 'LTE2275', 'LTE1638', 'LTEXYZ',
    'LBT2762_LBT2763', 'LTE1321', 'LTE1509', 'LTE2384', 'LTE2324', 'LTE1536', 'LTE648',
    'LTE2149', 'LTE1130', 'LTE1731', 'LTE1406', 'SHB', 'LTE1749', 'LTE1569', 'LTE1469',
    'LTE2161', 'LTE2014', 'LBT2989', 'LTE825', 'LBT2180', 'LTE2302']"""




    i = 0
    for dir in dir_list:
        thread1 = Thread(target=main, args=[i,
            {
                'testline_type' : 'CLOUD_F',
                'duration' : 600
            },
            {},
            {
                'parameters' :
                    {
                        'name' : dir
                    }
            },
            None,
            68880])
        i += 1
        thread1.start()
        thread1.join()


'''
