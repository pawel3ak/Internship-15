# -*- coding: utf-8 -*-
"""
:created on: '11/08/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nokia.com
"""

from supervisor_api import Supervisor

def main(serverID, reservation_data, parent_dict, jenkins_info, user_info = None, TLreservationID = None):
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

    if not supervisor.reservation_data['duration']:
        supervisor.failureStatus = 7
        supervisor.finish_with_failure()

    supervisor.get_TLreservationID()

    supervisor.set_parent_dict()
    supervisor.reservation_status()
    supervisor.set_TLname(supervisor.get_TLname_from_ID())
    supervisor.set_TLaddress(supervisor.get_TLaddress_from_ID())

    #############################################################################
    #temporary hard-coded  variables:
    print supervisor.set_TLname('tl99_test')
    print supervisor.set_TLaddress('wmp-tl99.lab0.krk-lab.nsn-rdnet.net')
    print supervisor.set_user_info('Pawel','Nogiec','pawel.nogiec@nokia.com')
    ##############################################################################

    supervisor.set_parent_dict()

    supervisor.set_job_api()
    if not supervisor.get_job_status() == None:
        supervisor.create_and_build_job()
    if not supervisor.get_job_status() == "SUCCESS":
        supervisor.send_information(test_status="UNKNOWN_FAIL")
        return 0
    supervisor.get_jenkins_console_output()

    job_tests_parsed_status = supervisor.get_job_tests_status()
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
                    'name' : 'LTEXYZ-new'
                }
        },
        TLreservationID=68503)
