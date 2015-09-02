# -*- coding: utf-8 -*-
"""
:created on: '11/08/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nokia.com
"""

from supervisor_api import Supervisor

def supervisor(serverID, reservation_data, parent_dict, jenkins_info, user_info = None, TLreservationID = None):
    supervisor_api = Supervisor(serverID, reservation_data, parent_dict, jenkins_info, user_info = user_info, TLreservationID = TLreservationID)
    supervisor_api.set_parent_dictionary(busy_status=True)
    if supervisor_api.TLreservationID == None:
        supervisor_api.TLreservationID = supervisor_api.create_reservation(
            testline_type=reservation_data['testline_type'],
            # reservation_data['enb_build'],        #no idea if we'll use this, so I'm leaving that for now
            # reservation_data['ute_build'],
            # reservation_data['sysimage_build'],
            # reservation_data['robotle_revision'],
            # reservation_data['state'],
            duration=reservation_data['duration'])

    supervisor_api.set_parent_dictionary(busy_status=True)
    supervisor_api.reservation_status()
    supervisor_api.set_TLname(supervisor_api.get_TLname_from_ID())
    supervisor_api.set_TLaddress(supervisor_api.get_TLaddress_from_ID())

    #############################################################################
    #temporary hard-coded  variables:
    print supervisor_api.set_TLname('tl99_test')
    print supervisor_api.set_TLaddress('wmp-tl99.lab0.krk-lab.nsn-rdnet.net')
    print supervisor_api.set_user_info('Pawel','Nogiec','pawel.nogiec@nokia.com')
    ##############################################################################

    supervisor_api.set_parent_dictionary()

    print supervisor_api.git_launch(pull_only=True)



    supervisor_api.set_job_api()
    if not supervisor_api.get_is_queue_or_running():
        supervisor_api.create_and_build_job()

    supervisor_api.get_jenkins_console_output()
    supervisor_api.get_job_status()

    supervisor_api.set_job_tests_failed_list()
    supervisor_api.set_parent_dictionary()

    print supervisor_api.ending()

    if supervisor_api.has_got_fail :
        supervisor_api.remove_tag_from_file()

    supervisor_api.send_information()

    supervisor_api.set_parent_dictionary(busy_status=False)
    return 0

