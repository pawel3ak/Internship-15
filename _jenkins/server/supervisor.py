
"""
:created on: '11/08/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nokia.com
"""

import tl_reservation as tlr
import time
import jenkinsapi
import xml.etree.ElementTree as ET
import re
import ute_mail.sender
import ute_mail.mail


def create_reservation_and_run_job(testline_type=None, enb_build=None, ute_build=None,
                                   sysimage_build=None, robotlte_revision=None,
                                   state=None, duration=None):

    reservation = tlr.TestLineReservation()
    return reservation.create_reservation(testline_type=testline_type, enb_build=enb_build,
                                                   ute_build=ute_build, sysimage_build=sysimage_build,
                                                   robotlte_revision=robotlte_revision,
                                                   state=state, duration=duration)

def reservation_status(id):
    reservation = tlr.TestLineReservation(id)
    reservation_status_dict = {1: 'Pending for testline',
                               2: 'Testline assigned',
                               3: 'Confirmed',
                               4: 'Finished',
                               5: 'Canceled'}
    while True:
        if reservation.get_reservation_status() == reservation_status_dict[1] or\
                        reservation.get_reservation_status() == reservation_status_dict[2]:
            print "jeszcze nie"
            time.sleep(30)
        elif reservation.get_reservation_status() == reservation_status_dict[3]:
            return 0
        elif reservation.get_reservation_status() == reservation_status_dict[4] or\
                        reservation.get_reservation_status() == reservation_status_dict[5]:
            raise "Reservation already canceled or finished"

def _get_tl_name(id):
    reservation = tlr.TestLineReservation(id)
    return reservation.get_reservation_details()['testline']['name']

def send_information(id,tl_name,user_info, test_passed = False):
    # user_info['first_name']
    # user_info['last_name']
    # user_info['e-mail']
    _message = "Hello {f_name} {l_name}! \n\n" \
                  "Your reservation is pending.\n" \
                  "Reservation ID = {rID}\n" \
                  "Testline name = {tl_name}\n\n" \
                  "Have a nice day!".format(f_name=user_info['first_name'],
                                            l_name=user_info['last_name'],
                                            rID=id, tl_name=tl_name)
    _subject = "Reservation status update"

    if test_passed == True:
        _message = "Hello {f_name} {l_name}! \n\n" \
                  "All your tests were successful\n\n" \
                  "Have a nice day!".format(f_name=user_info['first_name'],
                                            l_name=user_info['last_name'])
        _subject = "Tests status update"

    send = ute_mail.sender.SMTPMailSender(host = '10.150.129.55')
    mail = ute_mail.mail.Mail(subject=_subject,message=_message, recipients=user_info['e-mail'], name_from="Reservation Api")
    send.connect()
    send.send(mail)

def _update_tl_name(job, tl_name):
    job_config_xml = ET.fromstring(job.get_config())
    assignedNode_tag = job_config_xml.find('assignedNode')
    assignedNode_tag.text = str(tl_name)
    job.update_config(ET.tostring(job_config_xml))


def _create_and_build_job(jenkins_info, tl_name):
    _job_name = jenkins_info['name']
    job_parameters = jenkins_info['parameters']
    job_api = jenkinsapi.api.Jenkins('http://plkraaa-jenkins.emea.nsn-net.net:8080', username='nogiec', password='!salezjanierlz3!')
    job = job_api.get_job(_job_name)
    _update_tl_name(job, tl_name)
    job_api.build_job(jobname=_job_name, params=job_parameters)
    return job

def _get_jenkins_console_output(jenkins_info, job):
    time.sleep(5)       #let the new job build get started
    while job.get_last_build().get_status() == None:
        time.sleep(10)      ###############TODO longer sleep on real tests
    return (job.get_last_build().get_console()).split("\n")

def _update_parent_dict(serverID, parent_dict, id, job_test_status=None, busy_status = False):
    parent_dict[serverID] = {'reservationID' : id,
                             'busy' : busy_status,
                             'test_status' : job_test_status}

def _get_job_test_status(job_output):
    dict = {}
    has_got_fail = False
    for test in range(0,len(job_output)):
        try:
            match = re.search('^(.*)\s*.\sFAIL|^(.*)\s*.\sPASS',job_output[test]).groups()
            if match[0] != None:
                dict[match[0]] = 'FAIL'
                has_got_fail = True
            else:
                dict[str(match[1][:-1]).strip(" ")] = 'PASS'
        except:
            pass
    return dict, has_got_fail


def main(serverID, reservation_data, parent_dict, user_info, jenkins_info):

    reservationID = create_reservation_and_run_job(reservation_data['testline_type'],
                                                   reservation_data['enb_build'],
                                                   reservation_data['ute_build'],
                                                   reservation_data['sysimage_build'],
                                                   reservation_data['robotle_revision'],
                                                   reservation_data['state'],
                                                   reservation_data['duration'])
    print reservationID
    _update_parent_dict(serverID=serverID, parent_dict=parent_dict, id=reservationID, busy_status=True)
    if not reservation_status(reservationID) == 0:
        raise "Some weird exception"
    tl_name = _get_tl_name(reservationID)
    print tl_name
    send_information(reservationID, tl_name, user_info)
    job = _create_and_build_job(jenkins_info, tl_name)
    jenkins_console_output = _get_jenkins_console_output(jenkins_info, job)
    job_test_status_dict, has_got_fail = _get_job_test_status(job_output=jenkins_console_output)
    if has_got_fail:
        _update_parent_dict(serverID=serverID, parent_dict=parent_dict, id=reservationID,
                            job_test_status=job_test_status_dict, busy_status=True)
        #todo rerun robot with specifig tags
    else:
        _update_parent_dict(serverID=serverID, parent_dict=parent_dict, id=reservationID,
                            job_test_status=job_test_status_dict, busy_status=False)
        send_information(reservation_data, tl_name, user_info, test_passed=True)


# if __name__ == '__main__':
#     main()
    # reservationID = create_reservation_and_run_job(testline_type="CLOUD_F")
    # print reservationID
    # time.sleep(2)
    # print reservation_status(reservationID)
    # print _get_tl_name(reservationID)

    # jenkins_info = {'name' : 'test_job_tl_99',
    #                 'parameters' : {
    #                     'f_name' : 'ttt',
    #                     't1' : 'inny',
    #                     't2' : 'jeszcze_inny'},
    #                 }
    # job = _create_and_build_job(jenkins_info,tl_name="tl99_test")
    # jenkins_console_output = _get_jenkins_console_output(jenkins_info, job)
    # job_test_status_dict, has_got_fail = _get_job_test_status(jenkins_console_output)
    # print job_test_status_dict, has_got_fail

    # send_information(12343,"tl99",user_info={'first_name' : 'Pawel',
    #                                          'last_name' : 'Nogiec',
    #                                          'e-mail' : 'pawel.nogiec@nokia.com'})
    # send_information(12343,"tl99",user_info={'first_name' : 'Pawel',
    #                                          'last_name' : 'Nogiec',
    #                                          'e-mail' : 'pawel.nogiec@nokia.com'}, test_passed=True)
