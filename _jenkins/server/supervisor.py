# -*- coding: utf-8 -*-
"""
:created on: '11/08/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nokia.com
"""

from supervisor_api import Supervisor
import time

def main(serverID, reservation_data, parent_dict, jenkins_info, user_info = None, TLreservationID = None):
    # print serverID
    # print reservation_data
    # print parent_dict
    # print jenkins_info
    # print user_info
    # TLreservationID = 11214
    #jenkins_info['parameters']['name'] = "LTEXYZ"
    supervisor = Supervisor(serverID, reservation_data, parent_dict, jenkins_info, user_info = user_info, TLreservationID = TLreservationID)

    if supervisor.TLreservationID == None:
        supervisor.TLreservationID = supervisor.create_reservation_and_run_job(
            testline_type=reservation_data['testline_type'],
            # reservation_data['enb_build'],
            # reservation_data['ute_build'],
            # reservation_data['sysimage_build'],
            # reservation_data['robotle_revision'],
            # reservation_data['state'],
            duration=reservation_data['duration'])
    print supervisor.jenkins_info
    if not supervisor.reservation_data['duration']:
        supervisor.failureStatus = 7
        supervisor.finish_with_failure()
    print supervisor.TLreservationID
    time.sleep(2)
    supervisor.get_TLreservationID()

    supervisor.set_parent_dict(busy_status=True)
    # supervisor.reservation_status()
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
    if not supervisor.get_job_status() == None:
        supervisor.create_and_build_job()
    if not supervisor.get_job_status() == "SUCCESS":
        supervisor.finish_with_failure(test_status="UNKNOWN_FAIL")
        return 0
    supervisor.get_jenkins_console_output()


    job_tests_parsed_status = supervisor.get_job_tests_status()
    supervisor.set_parent_dict(busy_status=True, job_tests_parsed_status=job_tests_parsed_status)

    supervisor.ending()



    if supervisor.has_got_fail :
        for test in supervisor.parent_dict[supervisor.serverID]['test_status']:
            supervisor.remove_tag_from_file(directory=test['test_name'],
                                            file_name=test['file_name'],
                                            old_tag= 'enable'
                                            )

    supervisor.send_information()

    supervisor.set_parent_dict(busy_status=False, job_tests_parsed_status=job_tests_parsed_status)
    return 0

if __name__ == '__main__':
    main(serverID=69,
         reservation_data={
             'testline_type' : 'CLOUD_F',
             'duration' : 600
         },
        parent_dict={},
        jenkins_info={
            'parameters' :
                {
                    'name' : 'LTEXYZ'
                }
        },
        TLreservationID=68880)
