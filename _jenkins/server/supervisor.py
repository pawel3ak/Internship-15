
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
            time.sleep(60)
        elif reservation.get_reservation_status() == reservation_status_dict[3]:
            return 0
        elif reservation.get_reservation_status() == reservation_status_dict[4] or\
                        reservation.get_reservation_status() == reservation_status_dict[5]:
            return -1


def _get_tl_name(id):
    reservation = tlr.TestLineReservation(id)
    return reservation.get_reservation_details()['testline']['name']


def send_information(id,tl_name,user_info, test_passed = None, tests_status = None):
    if test_passed == None:
        _message = "Hello {f_name} {l_name}! \n\n" \
                   "Your reservation is pending.\n" \
                   "Reservation ID = {rID}\n" \
                   "Testline name = {tl_name}\n\n" \
                   "Have a nice day!".format(f_name=user_info['first_name'],
                                             _name=user_info['last_name'],
                                             rID=id, tl_name=tl_name)
        _subject = "Reservation status update"

    elif test_passed == True:
        _message = "Hello {f_name} {l_name}! \n\n" \
                  "All your tests were successful\n\n" \
                  "Have a nice day!".format(f_name=user_info['first_name'],
                                            l_name=user_info['last_name'])
        _subject = "Tests status update - finished"

    elif test_passed == False:
        test_info = ''
        for test_status_number in range(0, len(tests_status)):
            test_info += "Test = {test_name}.{file_name}\n".format(
                test_name=tests_status[test_status_number]['test_name'],
                file_name=tests_status[test_status_number]['file_name'])
        _message = "Hello {f_name} {l_name}! \n\n" \
                  "Few tests didn't pass: \n\n" \
                  "{test_info}\n\n" \
                  "Have a nice day!".format(f_name=user_info['first_name'],
                                            l_name=user_info['last_name'],
                                            test_info=test_info)
        _subject = "Tests status update - finished"

    send = ute_mail.sender.SMTPMailSender(host = '10.150.129.55')
    mail = ute_mail.mail.Mail(subject=_subject,message=_message, recipients=user_info['e-mail'], name_from="Reservation Api")
    send.connect()
    send.send(mail)


# def _update_tl_name(job, tl_name):
#     job_config_xml = ET.fromstring(job.get_config())
#     assignedNode_tag = job_config_xml.find('assignedNode')
#     assignedNode_tag.text = str(tl_name)
#     job.update_config(ET.tostring(job_config_xml))


def _create_and_build_job(jenkins_info, tl_name):
    _job_name = 'test_on_{tl_name}'.format(tl_name=tl_name)
    job_parameters = jenkins_info['parameters']
    job_api = jenkinsapi.api.Jenkins('http://plkraaa-jenkins.emea.nsn-net.net:8080', username='nogiec', password='!salezjanierlz3!')
    job = job_api.get_job(_job_name)
    # _update_tl_name(job, tl_name)
    job_api.build_job(jobname=_job_name, params=job_parameters)
    return job


def _get_jenkins_console_output(job):
    time.sleep(10)       #let the new job build get started
    while job.get_last_build().get_status() == None:
        time.sleep(30)      ###############TODO longer sleep on real tests
    return job.get_last_build().get_console()


def _update_parent_dict(serverID, parent_dict, id, busy_status, tl_name, duration, job_test_status=None):
    parent_dict[serverID]['reservationID'] = id
    parent_dict[serverID]['busy'] = busy_status
    parent_dict[serverID]['tl_name'] = tl_name
    parent_dict[serverID]['duration'] = duration
    parent_dict[serverID]['test_status'] = job_test_status


def _get_job_test_status(job_output):
    has_got_fail = False
    regex = r'[=]\s(.*)\s[=]\W*.*FAIL'
    match = re.findall(regex,job_output)
    if len(match) != 0: has_got_fail = True
    tests_dict=[]
    for i in range(0,len(match)):
        match[i] = re.sub(" +", "_", match[i])
        if match[i][-3:] == '...': match[i] = match[i][:-3]
        if match[i][-1:] == '_': match[i] = match[i][:-1]
        try:
            match[i] = re.search('CPLN\.(\w*)\.Tests\.(.*)', match[i]).groups()
            tests_dict.append({'test_name' : match[i][0],
                          'file_name' : match[i][1]})
        except:
            match[i] = re.search('CPLN\.(\w*)\.(.*)', match[i]).groups()
            tests_dict.append({'test_name' : match[i][0],
                          'file_name' : match[i][1]})

    return tests_dict, has_got_fail


def _check_for_fails(output):
    return output.find('| FAIL |')


def _end(id, has_got_fail, tl_name, user_info, job_test_status, jenkins_console_output=None):
    if has_got_fail == False:
        if _check_for_fails(jenkins_console_output) == -1: test_passed = True
        else: test_passed = "UNKNOWN_FAIL"
    else:
        test_passed = False

    send_information(id, tl_name, user_info, test_passed, job_test_status)
    return 0


def main(serverID, reservation_data, parent_dict, user_info, jenkins_info):
    reservationID = create_reservation_and_run_job(reservation_data['testline_type'],
                                                   reservation_data['enb_build'],
                                                   reservation_data['ute_build'],
                                                   reservation_data['sysimage_build'],
                                                   reservation_data['robotle_revision'],
                                                   reservation_data['state'],
                                                   reservation_data['duration'])
    _update_parent_dict(serverID=serverID, parent_dict=parent_dict, id=reservationID, busy_status=True,
                        tl_name='', duration=reservation_data['duration'])
    if not reservation_status(reservationID) == 0:
        parent_dict[serverID]['busy'] = False
        return -1
    tl_name = _get_tl_name(reservationID)

    ############################################################################
    #temporary hard-coded  variables:
    tl_name = 'tl_99_test'
    user_info = {'first_name' : 'Pawel',
                'last_name' : 'Nogiec',
                'e-mail' : 'pawel.nogiec@nokia.com'}
    #############################################################################
    _update_parent_dict(serverID=serverID, parent_dict=parent_dict, id=reservationID, busy_status=True,
                        tl_name=tl_name, duration=reservation_data['duration'])

    job = _create_and_build_job(jenkins_info, tl_name)
    jenkins_console_output = _get_jenkins_console_output(job)
    job_test_status_dict, has_got_fail = _get_job_test_status(job_output=jenkins_console_output)
    _end(id=reservationID, has_got_fail=has_got_fail, tl_name=tl_name,
         job_test_status=job_test_status_dict, user_info=user_info)
    return 0
