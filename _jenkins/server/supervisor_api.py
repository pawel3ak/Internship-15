# -*- coding: utf-8 -*-
"""
:created on: '11/08/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nokia.com
"""

import time
import xml.etree.ElementTree as ET
import re
import os
import sys
import logging

import jenkinsapi
import ute_mail.sender
import ute_mail.mail
import paramiko

import tl_reservation as tlr
from mailing_list import mail_dict
from utilities.logger_messages import LOGGER_INFO
from server_git_api import git_launch

# create logger
logger = logging.getLogger("server." + __name__)


class Supervisor(object):
    def __init__(self, serverID, reservation_data, parent_dict, jenkins_info, user_info=None, TLreservationID=None):
        self.serverID = serverID
        if not 'duration' in reservation_data:
            self.failureStatus = 113
            logger.error('{}'.format(LOGGER_INFO[self.failureStatus]))
            self.finish_with_failure()
        self.reservation_data = reservation_data
        self.parent_dictionary = parent_dict    #dictionary used to communicate with parent process
        self.jenkins_info = jenkins_info
        self.TLreservationID = TLreservationID
        self.user_info = user_info
        self.TLname = None
        self.TLaddress = None
        self.failureStatus = None
        self.are_any_failed_tests = False
        self.test_end_status = None
        self.job_tests_failed_list = None
        logger.debug("Created new Supervisor object with args: "
                     "serverID = {}, reservation_data = {}, parent_dict = {}, jenkins_info = {}, user_info = {},"
                     " TLreservationID = {}".format(self.serverID, self.reservation_data, self.parent_dictionary,
                                                    self.jenkins_info, self.user_info, self.TLreservationID))


    def get_serverID(self):
        return self.serverID

    def get_reservation_data(self):
        return self.reservation_data

    def get_parent_dictionary(self):
        return self.parent_dictionary

    def set_parent_dictionary(self, busy_status=True):
        '''
        :param busy_status: tells whether supervisor has finished work or not
        :return self.parent_dictionary: full information about reservation that is managed by this supervisor
        '''
        jenkins_info = self.jenkins_info.copy()
        if 'job_api' in jenkins_info:
            del jenkins_info['job_api']
        if 'console_output' in jenkins_info:
            del jenkins_info['console_output']
        self.parent_dictionary[self.serverID] = {
            'reservationID' : self.TLreservationID,
            'busy_status' : busy_status,
            'tl_name' : self.TLname,
            'duration' : self.reservation_data['duration'],
            'test_status' : self.job_tests_failed_list,
            'jenkins_info': jenkins_info,
            'reservation_data' : self.reservation_data,
            'user_info' : self.user_info
        }
        logger.debug("Parent dictionary = {}".format(self.parent_dictionary))
        return self.parent_dictionary

    def get_jenkins_info(self):
        return self.jenkins_info


    def get_TLreservationID(self):
        return self.TLreservationID

    def get_user_info(self):
        return self.user_info

    def set_user_info(self, first_name, last_name, e_mail):
        self.user_info = {
            'first_name' : first_name,
            'last_name' : last_name,
            'e-mail' :e_mail
        }
        logger.debug("Saving user informations : {} {}, email: {}".format(first_name,last_name,e_mail))

        return self.user_info

    def get_TLname(self):
        return self.TLname

    def set_TLname_from_TLreservationID(self):
        reservation = tlr.TestLineReservation(self.TLreservationID)
        self.TLname = reservation.get_reservation_details()['testline']['name']
        return self.TLname

    def set_TLname(self,name):
        self.TLname = name
        return self.TLname

    def get_TLaddress_from_ID(self):
        reservation = tlr.TestLineReservation(self.TLreservationID)
        return reservation.get_address()

    def get_TLaddress(self):
        return self.TLaddress

    def set_TLaddress(self, address):
        self.TLaddress = address
        return self.TLaddress

    def finish_with_failure(self, test_status = None):
        self.parent_dictionary[self.serverID]['busy_status'] = False
        if test_status:
            self.test_end_status = test_status
        self.send_information_about_executed_job(test_status=self.test_end_status)
        sys.exit()

    def create_reservation(self, testline_type=None, enb_build=None, ute_build=None,
                                   sysimage_build=None, robotlte_revision=None,
                                   state=None, duration=None):

        reservation = tlr.TestLineReservation()

        self.TLreservationID = reservation.create_reservation(testline_type=testline_type, enb_build=enb_build,
                                                           ute_build=ute_build, sysimage_build=sysimage_build,
                                                           robotlte_revision=robotlte_revision,
                                                           state=state, duration=duration)
        if self.TLreservationID == -103:
            self.failureStatus = 101
            logger.warning('{}'.format(LOGGER_INFO[self.failureStatus]))
            self.finish_with_failure(test_status="PASS")
        elif self.TLreservationID == -102:
            self.failureStatus = 102
            logger.warning('{}'.format(LOGGER_INFO[self.failureStatus]))
            self.finish_with_failure(test_status="PASS")
        else:
            logger.info("Reservation created. ID: {}".format(self.TLreservationID))
            return self.TLreservationID

    def check_and_wait_for_TL_being_prepared_to_use(self):
        reservation = tlr.TestLineReservation(self.TLreservationID)
        _reservation_status_dict = {1: 'Pending for testline',
                                   2: 'Testline assigned',
                                   3: 'Confirmed',
                                   4: 'Finished',
                                   5: 'Canceled'}
        while True:
            if reservation.get_reservation_status() == _reservation_status_dict[1] or\
                            reservation.get_reservation_status() == _reservation_status_dict[2]:
                logger.debug("Waiting for TL (reservation ID: {}) to be ready for use. TL status: {}".format(self.TLreservationID, reservation.get_reservation_status()))
                time.sleep(120)
            elif reservation.get_reservation_status() == _reservation_status_dict[3]:
                logger.info("{} ready".format(self.set_TLname_from_TLreservationID()))
                return 0
            elif reservation.get_reservation_status() == _reservation_status_dict[4] or\
                            reservation.get_reservation_status() == _reservation_status_dict[5]:
                self.failureStatus = 103
                logger.warning('{} {}'.format(self.TLreservationID, LOGGER_INFO[self.failureStatus]))
                self.finish_with_failure()


    def set_job_TLname(self):
        try:
            job = self.jenkins_info['job_api'].get_job(self.jenkins_info['job_name'])
            job_config_xml = ET.fromstring(job.get_config())
            assignedNode_tag = job_config_xml.find('assignedNode')
            assignedNode_tag.text = str(self.TLname)
            job.update_config(ET.tostring(job_config_xml))
            logger.debug("Updated TL name: {} in job {}".format(self.TLname, self.jenkins_info['job_name']))
            return 0
        except:
            self.failureStatus = 104
            logger.warning('{} : {}'.format(self.TLname, LOGGER_INFO[self.failureStatus]))
            self.finish_with_failure()

    def get_job_status(self):
        job_status = None
        try:
            job = self.jenkins_info['job_api'].get_job(self.jenkins_info['job_name'])
            job_status = job.get_last_build().get_status()
        except:
            self.failureStatus = 105
            logger.error('{} : {}'.format(self.jenkins_info['job_name'],LOGGER_INFO[self.failureStatus]))
            self.finish_with_failure()
        finally:
            logger.debug("Job {} status = {}".format(self.jenkins_info['job_name'], job_status))
            if job_status == "FAILURE":
                self.are_any_failed_tests = False
                self.check_output_for_other_fails_or_errors_and_get_test_end_status()
            else:
                return job.get_last_build().get_status()

    def is_queued_or_running(self):
        try:
            job = self.jenkins_info['job_api'].get_job(self.jenkins_info['job_name'])
            return job.is_queued_or_running()
        except:
            self.failureStatus = 105
            logger.error('{} : {}'.format(self.jenkins_info['job_name'],LOGGER_INFO[self.failureStatus]))
            self.finish_with_failure()

    def set_job_api(self):
        if not 'job_name' in self.jenkins_info:
            self.jenkins_info['job_name'] = 'test_on_{tl_name}'.format(tl_name=self.TLname)
        try:
            job_api = jenkinsapi.api.Jenkins('http://plkraaa-jenkins.emea.nsn-net.net:8080', username='nogiec', password='!salezjanierlz3!')
            self.jenkins_info['job_api'] = job_api
            logger.debug("job_api has been set")
            return self.jenkins_info['job_api']
        except:
            self.failureStatus = 106
            logger.critical('{}'.format(LOGGER_INFO[self.failureStatus]))
            self.finish_with_failure()

    def create_and_build_job(self):
        try:
            self.set_job_TLname()
            self.jenkins_info['job_api'].build_job(jobname=self.jenkins_info['job_name'],
                                                   params=self.jenkins_info['parameters'])
            logger.info("Job {} was built".format(self.jenkins_info['job_name']))
            return 0
        except:
            self.failureStatus = 107
            logger.error('{}'.format(LOGGER_INFO[self.failureStatus]))
            self.finish_with_failure()

    def get_jenkins_console_output(self):
        try:
            job = self.jenkins_info['job_api'].get_job(self.jenkins_info['job_name'])
            while True:
                if not self.is_queued_or_running(): break
                else:
                    time.sleep(2)   ####TODO longer time on real tests
            self.jenkins_info['console_output'] = job.get_last_build().get_console()
            logger.debug("Console output retrieved from {}".format(self.jenkins_info['job_name']))
            return self.jenkins_info['console_output']
        except:
            self.failureStatus = 108
            logger.error('{}'.format(LOGGER_INFO[self.failureStatus]))
            self.finish_with_failure()

    def set_job_tests_failed_list(self):
        regex = r'\=\s(.*)\s\=\W*.*FAIL'
        job_tests_failed_list=[]
        try:
            matches = re.findall(regex,self.jenkins_info['console_output'])
            if len(matches) != 0: self.are_any_failed_tests = True
            for match in matches:
                match = re.sub(" +", "_", match)  #changing " " to "_" - pybot thinks it's the same, i don't
                if match[-3:] == '...': match = match[:-3]  #cutting last "..."
                if match[-1:] == '_': match = match[:-1]    #cutting last "_"
                try:
                    match = re.search('(\w*)\.Tests\.(.*)', match).groups()
                    job_tests_failed_list.append({'test_name' : match[0],
                                  'file_name' : match[1]})
                except:
                    match = re.search('(\w*)\.(.*)', match).groups()
                    job_tests_failed_list.append({'test_name' : match[0],
                                       'file_name' : match[1]})
            logger.info("Regex found fails in output of {}".format(self.jenkins_info['job_name']))
        except:
            logger.debug("Regex did not find fails in output of {}".format(self.jenkins_info['job_name']))
            pass
        finally:
            self.job_tests_failed_list = job_tests_failed_list
            return self.job_tests_failed_list

    def check_for_fails(self):
        output = str(self.jenkins_info['console_output'])
        if not output.find('| FAIL |') == -1:
            logger.debug("Found 'FAIL' in output of {}".format(self.jenkins_info['job_name']))
            return False
        output = output.split('\n')
        for line in output:
            if re.findall('\[.ERROR.\].*no tests.*', line):
                ###mozna zapisac, ze tag ciagle nie zmieniony i wysylac ponownie mail do testerow
                continue
            if not line.find('[ ERROR ]') == -1:
                logger.debug("Found 'ERROR' in output of {}".format(self.jenkins_info['job_name']))
                return False
        return True

    def check_output_for_other_fails_or_errors_and_get_test_end_status(self):
        if not self.are_any_failed_tests:
            if self.check_for_fails() == True:
                self.test_end_status = "PASS"
                logger.info("Test {} was successful".format(self.jenkins_info['job_name']))
            else:
                self.test_end_status = "UNKNOWN_FAIL"
                self.are_any_failed_tests = True
                self.failureStatus = 109
                logger.error('{}'.format(LOGGER_INFO[self.failureStatus]))
                self.finish_with_failure(test_status=self.test_end_status)
        else:
            self.test_end_status = "Failed"
            self.are_any_failed_tests = True
            logger.info("Test {} has got some failures".format(self.jenkins_info['job_name']))
        return self.test_end_status

    def get_SSHClient_connection(self):
        SSHClient = paramiko.SSHClient()
        SSHClient .load_system_host_keys()
        SSHClient .set_missing_host_key_policy(paramiko.AutoAddPolicy())
        SSHClient .connect(self.get_TLaddress(), username='ute', password='ute')
        return SSHClient

    def _check_if_more_directories(self):           #is private?
        additional_directory_list = []
        files_names_list = []
        for test in self.parent_dictionary[self.serverID]['test_status']:
            try:
                match = re.search('({}.*)\.({}.*)'.format(test['test_name'],test['test_name']),
                                                test['file_name']).groups()
                additional_directory_list.append(match[0])
                files_names_list.append(match[1])
            except:
                files_names_list.append(test['file_name'])
                additional_directory_list.append('')

    def _try_to_match_file_name(self, additional_directory_list, files_names_list):         #is private?
        for i in range(len(files_names_list)):
            if additional_directory_list[i] == '':
                path = '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/{}/tests/'.format(
                    self.parent_dictionary[self.serverID]['test_status'][i]['test_name'])
            else:
                path = '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/{}/tests/{}'.format(
                    self.parent_dictionary[self.serverID]['test_status'][i]['test_name'],
                    additional_directory_list[i])
            try:
                SSHClient = self.get_SSHClient_connection()
                files = SSHClient.open_sftp().listdir(path=path)
                SSHClient.close()
                found = False
                for file in files:
                    try:
                        file_name = re.search('({name}.*)'.format(name=files_names_list[i]),file).groups()[0]
                        found = True
                        self.parent_dictionary[self.serverID]['test_status'][i]['file_name'] = file_name
                        logger.debug("Found filename: {}".format(file_name))
                        break
                    except:
                        pass
                if not found:
                    self.failureStatus = 110
                    logger.warning('{}'.format(LOGGER_INFO[self.failureStatus]))
            except:
                pass

    def remove_tag_from_robots_tests(self, old_tag = 'enable', new_tag = ''):
        additional_directory_list, files_names_list = self._check_if_more_directories()
        path, file_name = self._try_to_match_file_name(additional_directory_list, files_names_list)

        try:
            SSHClient = self.get_SSHClient_connection()
            file = SSHClient.open_sftp().open(os.path.join(path, file_name), 'r')
            lines_in_file = file.readlines()
            file.close()
            SSHClient.close()
            found = False
            for line in range(0, len(lines_in_file)):
                try:
                    tag_line = re.search('\[Tags](.*)', lines_in_file[line]).groups()[0]
                    try:
                        lines_in_file[line] = re.sub(old_tag, new_tag, lines_in_file[line])
                        found = True
                        logger.debug("Changed tag in file: {} from {} to {}".format(file_name, old_tag, new_tag))
                    except:
                        pass
                except:
                    pass
            if not found:
                self.failureStatus = 111
                logger.warning('{} : {}'.format(LOGGER_INFO[self.failureStatus], old_tag))
            git_result = self.git_launch(file_info=[path, file_name])
            if not git_result == True:
                self.failureStatus = 114
                logger.warning('{} : {}'.format(LOGGER_INFO[self.failureStatus], git_result))
            logger.info("Git push successful on {}".format(self.TLname))
            SSHClient = self.get_SSHClient_connection()
            file = SSHClient.open_sftp().open(os.path.join(path,file_name), 'w')
            file.writelines(lines_in_file)
            file.close()
            SSHClient.close()
        except:
            self.failureStatus = 112
            logger.warning('{}'.format(LOGGER_INFO[self.failureStatus]))

    def send_information_about_executed_job(self, test_status=None):
        if test_status:
            self.test_end_status = test_status
        if self.test_end_status == "PASS":
            return 0
        elif self.test_end_status == None:
            self.test_end_status = 'UNKNOWN_FAIL'

        messages = []
        subject = ""
        if self.test_end_status == "reserv_pending":
            _message = "Dear {f_name} {l_name}! \n\n" \
                       "Your reservation is pending.\n" \
                       "Reservation ID = {rID}\n" \
                       "Testline name = {tl_name}\n\n" \
                       "Have a nice day!".format(f_name=self.user_info['first_name'],
                                                 l_name=self.user_info['last_name'],
                                                 rID=self.TLreservationID, tl_name=self.TLname)
            messages.append({'message' : _message})
            subject = "Reservation status update"


        elif self.test_end_status == "Failed":
            job = self.jenkins_info['job_api'].get_job(self.jenkins_info['job_name'])
            t = job.get_last_build().get_timestamp()
            build_time = '{}-{:02g}-{:02g}_{:02g}-{:02g}-{:02g}'.format(t.year, t.month, t.day, (t.hour-(time.altzone/3600)), t.minute, t.second)
            logs_link = 'http://10.83.200.35/~ltebox/logs/{}_{}/log.html'.format(self.TLname, build_time)
            test_info = ''
            print "test_status = ", self.parent_dictionary[self.serverID]['test_status']

            for test in self.parent_dictionary[self.serverID]['test_status']:
                test_info += "Test = {test_name}.{file_name}\n".format(
                    test_name=test['test_name'],
                    file_name=test['file_name'])
            _message = "Dear tester! \n\n" \
                        "Your test have failed: \n\n" \
                        "{test_info}\n\n" \
                        "Logs are available at: {logs_link}\n\n" \
                        "Have a nice day!".format(test_info=test_info,
                                                  logs_link=logs_link)
            messages.append({'message' : _message,
                            'feature' : self.parent_dictionary[self.serverID]['test_status'][0]['test_name']})
            subject = "Tests status update - finished with fail"


        elif self.test_end_status == 'UNKNOWN_FAIL':
            job = self.jenkins_info['job_api'].get_job(self.jenkins_info['job_name'])
            logs_link = '{url}/job/{job_name}/{bn}/console'.format(url= 'http://plkraaa-jenkins.emea.nsn-net.net:8080',
                                                                  job_name=self.jenkins_info['job_name'],
                                                                  bn=job.get_last_buildnumber())
            _message = "Dear {f_name} {l_name}! \n\n" \
                       "Your test on {tl_name} has occured unknown fail.\n" \
                       "Please check logs available at: {logs_link} \n\n" \
                       "Have a nice day!".format(f_name=self.user_info['first_name'],
                                                 l_name=self.user_info['last_name'],
                                                 tl_name=self.TLname,
                                                 logs_link=logs_link)
            messages.append({'message' : _message})
            subject = "Tests status update - finished with unknown fail"




        if 'feature' in messages[0]:
            for message in messages:
                mail = ute_mail.mail.Mail(subject=subject,message=message['message'],
                                          recipients=mail_dict[message['feature']],
                                          name_from="Reservation Api")
                print mail_dict[message['feature']]
                send = ute_mail.sender.SMTPMailSender(host = '10.150.129.55')
                send.connect()
                send.send(mail)
        else:
            mail = ute_mail.mail.Mail(subject=subject,message=messages[0]['message'],
                                          recipients='pawel.nogiec@nokia.com',  #Bartek Kukla (?) mail here
                                          name_from="Reservation Api")          #We need to figure out better name
            send = ute_mail.sender.SMTPMailSender(host = '10.150.129.55')
            send.connect()
            send.send(mail)

    def git_launch(self, file_info=None, pull_only=None):
        return git_launch(TL_address=self.TLaddress, file_info=file_info, pull_only=pull_only)
