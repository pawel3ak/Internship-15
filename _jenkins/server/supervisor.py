
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
import os
import paramiko


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

def _get_tl_address(id):
    reservation = tlr.TestLineReservation(id)
    return reservation.get_address()


def send_information(id,tl_name,user_info, test_passed = None, tests_status = None):
    if test_passed == None:
        _message = "Dear {f_name} {l_name}! \n\n" \
                   "Your reservation is pending.\n" \
                   "Reservation ID = {rID}\n" \
                   "Testline name = {tl_name}\n\n" \
                   "Have a nice day!".format(f_name=user_info['first_name'],
                                             l_name=user_info['last_name'],
                                             rID=id, tl_name=tl_name)
        _subject = "Reservation status update"

    elif test_passed == True:
        _message = "Dear {f_name} {l_name}! \n\n" \
                   "Your job on {tl_name} were successful\n\n" \
                   "Have a nice day!".format(f_name=user_info['first_name'],
                                             l_name=user_info['last_name'],
                                             tl_name=tl_name)
        _subject = "Tests status update - finished"

    elif test_passed == False:
        test_info = ''
        for test_status_number in range(0, len(tests_status)):
            test_info += "Test = {test_name}.{file_name}\n".format(
                test_name=tests_status[test_status_number]['test_name'],
                file_name=tests_status[test_status_number]['file_name'])
        _message = "Dear {f_name} {l_name}! \n\n" \
                   "Few tests didn't pass: \n\n" \
                   "{test_info}\n\n" \
                   "Have a nice day!".format(f_name=user_info['first_name'],
                                             l_name=user_info['last_name'],
                                             test_info=test_info)
        _subject = "Tests status update - finished with fail"

    elif test_passed == 'UNKNOWN_FAIL':
        _message = "Dear {f_name} {l_name}! \n\n" \
                   "Your test on {tl_name} has failed but we couldn't catch where. " \
                   "Please check logs available at: {logs_link} \n\n" \
                   "Have a nice day!".format(f_name=user_info['first_name'],
                                            l_name=user_info['last_name'],
                                            tl_name=tl_name,
                                            logs_link="")
        _subject = "Tests status update - finished with fail"


    send = ute_mail.sender.SMTPMailSender(host = '10.150.129.55')
    mail = ute_mail.mail.Mail(subject=_subject,message=_message, recipients=user_info['e-mail'], name_from="Reservation Api")
    send.connect()
    send.send(mail)


def _update_tl_name(job, tl_name):
    job_config_xml = ET.fromstring(job.get_config())
    assignedNode_tag = job_config_xml.find('assignedNode')
    assignedNode_tag.text = str(tl_name)
    job.update_config(ET.tostring(job_config_xml))

def get_job_status(jenkins_info, tl_name):
    if 'job_name' in jenkins_info:
        _job_name = jenkins_info['job_name']
    else:
        _job_name = 'test_on_{tl_name}'.format(tl_name=tl_name)
    job_api = jenkinsapi.api.Jenkins('http://plkraaa-jenkins.emea.nsn-net.net:8080', username='nogiec', password='!salezjanierlz3!')
    job = job_api.get_job(_job_name)
    return job.get_last_build().get_status()

def _create_and_build_job(jenkins_info, tl_name):
    if 'job_name' in jenkins_info:
        _job_name = jenkins_info['job_name']
    else:
        _job_name = 'test_on_{tl_name}'.format(tl_name=tl_name)
    job_parameters = jenkins_info['parameters']
    job_api = jenkinsapi.api.Jenkins('http://plkraaa-jenkins.emea.nsn-net.net:8080', username='nogiec', password='!salezjanierlz3!')
    job = job_api.get_job(_job_name)
    _update_tl_name(job, tl_name)
    job_api.build_job(jobname=_job_name, params=job_parameters)
    return job


def _get_jenkins_console_output(job):
    time.sleep(10)       #let the new job build get started
    while job.get_last_build().get_status() == None:
        time.sleep(30)      ###############TODO longer sleep on real tests
    return job.get_last_build().get_console()


def _update_parent_dict(serverID, parent_dict, id, busy_status, tl_name, duration, job_test_status=None):
    parent_dict[serverID]={
        'reservationID' : id,
        'busy_status' : busy_status,
        'tl_name' : tl_name,
        'duration' : duration,
        'test_status' : job_test_status}


def _get_job_test_status(job_output):
    has_got_fail = False
    regex = r'\=\s(.*)\s\=\W*.*FAIL'
    try:
        match = re.findall(regex,job_output)
        if len(match) != 0: has_got_fail = True
        tests_failed_list_with_dict=[]
        for i in range(0,len(match)):
            match[i] = re.sub(" +", "_", match[i])
            if match[i][-3:] == '...': match[i] = match[i][:-3]
            if match[i][-1:] == '_': match[i] = match[i][:-1]
            try:
                match[i] = re.search('(\w*)\.Tests\.(.*)', match[i]).groups()
                tests_failed_list_with_dict.append({'test_name' : match[i][0],
                              'file_name' : match[i][1]})
            except:
                match[i] = re.search('(\w*)\.(.*)', match[i]).groups()
                tests_failed_list_with_dict.append({'test_name' : match[i][0],
                                   'file_name' : match[i][1]})
    except:
        tests_failed_list_with_dict = None

    return tests_failed_list_with_dict, has_got_fail


def _check_if_no_fails(output):
    try:
        if output.find('| FAIL |') == -1:
            return True
    except:
        try:
            if output.find('[ ERROR ]') == -1:
                return True
        except:
            pass
    return False


def _end(id, has_got_fail, tl_name, user_info, job_test_status, jenkins_console_output=None):
    if not has_got_fail:
        if _check_if_no_fails(jenkins_console_output) == True: test_passed = True
        else: test_passed = "UNKNOWN_FAIL"
    else:
        test_passed = False

    send_information(id=id, tl_name=tl_name, user_info=user_info, test_passed=test_passed,
                     tests_status=job_test_status)
    return 0

def remove_tag_from_file(tl_address, folder_name, file_name, old_tag, new_tag = ''):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy)
    client.connect(tl_address, username='ute', password='ute')
    sftp = client.open_sftp()
    path = '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/{}/tests/'.format(folder_name)
    try:
        files = sftp.listdir(path=path)
        found = False
        for file in range(0,len(files)):
            try:
                file_name = re.search('({name}.*)'.format(name=file_name),files[file]).groups()[0]
                found = True
                break
            except:
                pass
        if not found: return -1

        file = sftp.open(os.path.join(path,file_name), 'r')
        lines_in_file = file.readlines()

        found = False
        for line in range(0, len(lines_in_file)):
            try:
                tag_line = re.search('\[Tags](.*)', lines_in_file[line]).groups()[0]
                try:
                    lines_in_file[line] = re.sub(old_tag, new_tag, lines_in_file[line])
                    found = True
                except:
                    pass
            except:
                pass
        if not found: return -1
        file.close()
        file = sftp.open(os.path.join(path,file_name), 'w')
        file.writelines(lines_in_file)
        file.close()
    except:
        return -1
    finally:
        client.close()


def main(serverID, reservation_data, parent_dict, user_info, jenkins_info, reservationID = None):
    if not reservationID:
        reservationID = create_reservation_and_run_job(
            testline_type=reservation_data['testline_type'],
            # reservation_data['enb_build'],
            # reservation_data['ute_build'],
            # reservation_data['sysimage_build'],
            # reservation_data['robotle_revision'],
            # reservation_data['state'],
            duration=reservation_data['duration'])

    if not reservation_data['duration']: return -1

    print reservationID
    _update_parent_dict(serverID=serverID, parent_dict=parent_dict, id=reservationID, busy_status=True,
                        tl_name='', duration=reservation_data['duration'])
    if not reservation_status(reservationID) == 0:
        parent_dict[serverID]['busy'] = False
        return -1
    tl_name = _get_tl_name(reservationID)
    tl_address = _get_tl_address(reservationID)

    ############################################################################
    #temporary hard-coded  variables:
    tl_name = 'tl99_test'
    tl_address = 'wmp-tl99.lab0.krk-lab.nsn-rdnet.net'
    user_info = {'first_name' : 'Pawel',
                'last_name' : 'Nogiec',
                'e-mail' : 'pawel.nogiec@nokia.com'}
    #############################################################################
    _update_parent_dict(serverID=serverID, parent_dict=parent_dict, id=reservationID, busy_status=True,
                        tl_name=tl_name, duration=reservation_data['duration'])
    job_status = get_job_status(jenkins_info, tl_name)
    if not job_status == None:
        job = _create_and_build_job(jenkins_info, tl_name)
    jenkins_console_output = _get_jenkins_console_output(job)
    job_test_status_dict, has_got_fail = _get_job_test_status(job_output=jenkins_console_output)
    _end(id=reservationID, has_got_fail=has_got_fail, tl_name=tl_name,
         job_test_status=job_test_status_dict, user_info=user_info)
    _update_parent_dict(serverID=serverID, parent_dict=parent_dict, id=reservationID, busy_status=False,
                        tl_name=tl_name, duration=reservation_data['duration'])
    if has_got_fail:
        for test in range(0,len(job_test_status_dict)):
            remove_tag_from_file(tl_address = tl_address, folder_name=jenkins_info['parameters']['name'],
                                 file_name=str(job_test_status_dict[test]['file_name']),
                                 old_tag= 'enable')
    return 0


if __name__=='__main__':

    main(69,reservation_data={'testline_type' : 'CLOUD_F',
                              'duration' : 600},
        parent_dict={}, user_info=None, jenkins_info={'parameters' : {'name' : 'LTEXYZ'}},
        reservationID=67917)
