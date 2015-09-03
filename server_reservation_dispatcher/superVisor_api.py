
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

from mailing_list import mail_dict
from utilities.logger_messages import LOGGER_INFO
from server_git_api import git_launch

# create logger
logger = logging.getLogger("server." + __name__)
#######################################################################################
# temporary
from utilities.logger_config import config_logger
config_logger(logger)
########################################################################################

class Supervisor(object):
    def __init__(self,TLname, jenkins_job_info, user_info=None):
        self.jenkins_info = jenkins_job_info    #dict:{job_name : "", parameters : {param1 : "", ...}}
        self.user_info = user_info          #dict:{first_name : "", last_name : "", mail :""}
        self.TLname = TLname
        self.TLaddress = self.get_TLaddress()
        self.suitname = jenkins_job_info['parameters']['name']
        self.failureStatus = None
        self.are_any_failed_tests = False
        self.test_end_status = None
        self.job_filenames_failed_tests = None
        logger.debug("Created new Supervisor object with args: "
                     "jenkins_info = {}, user_info = {}, TLreservationID = {}".format(self.jenkins_info,
                                                                                      self.user_info,
                                                                                      self.TLreservationID))

    def get_jenkins_info(self):
        return self.jenkins_info


    def get_user_info(self):
        return self.user_info


    def get_TLname(self):
        return self.TLname


    def get_TLaddress(self):
        #TODO: open file with mapped TL->DNS_address and return address
        pass


    def finish_with_failure(self):
        #TODO clear job_info from file
        self.send_information_about_executed_job(test_status=self.test_end_status)
        sys.exit()


    def set_jenkins_connection(self):
        if not 'job_name' in self.jenkins_info:
            self.jenkins_info['job_name'] = 'job_on_{tl_name}'.format(tl_name=self.TLname)
        try:
            jenkins_connection = jenkinsapi.api.Jenkins('http://plkraaa-jenkins.emea.nsn-net.net:8080', username='nogiec', password='!salezjanierlz3!')
            self.jenkins_info['connection'] = jenkins_connection
            logger.debug("jenkins connection has been set")
            return self.jenkins_info['connection']
        except:
            self.failureStatus = 106
            self.test_end_status = "JenkinsError"
            logger.critical('{}'.format(LOGGER_INFO[self.failureStatus]))
            self.finish_with_failure()


    def set_jenkins_job(self):
        try:
            self.jenkins_info['job_handler'] = self.jenkins_info['connection'].get_job(self.jenkins_info['job_name'])
            return self.jenkins_info['job_handler']
        except:
            self.failureStatus = 125
            self.test_end_status = "JenkinsError"
            logger.critical('{}'.format(LOGGER_INFO[self.failureStatus]))
            self.finish_with_failure()


    def set_node_for_job(self):
        try:
            job = self.jenkins_info['job_handler']
            job_config_xml = ET.fromstring(job.get_config())
            assignedNode_tag = job_config_xml.find('assignedNode')
            assignedNode_tag.text = str(self.TLname)
            job.update_config(ET.tostring(job_config_xml))
            logger.debug("Updated TL name: {} in job {}".format(self.TLname, self.jenkins_info['job_name']))
            return 0
        except:
            self.failureStatus = 104
            self.test_end_status = "JenkinsError"
            logger.warning('{} : {}'.format(self.TLname, LOGGER_INFO[self.failureStatus]))
            self.finish_with_failure()


    def get_job_status(self):
        job_status = None
        try:
            job_status = self.jenkins_info['job_handler'].get_last_build().get_status()
        except:
            self.failureStatus = 105
            self.test_end_status = "JenkinsError"
            logger.error('{} : {}'.format(self.jenkins_info['job_name'],LOGGER_INFO[self.failureStatus]))
            self.finish_with_failure()
        finally:
            logger.debug("Job {} status = {}".format(self.jenkins_info['job_name'], job_status))
            if job_status == "FAILURE":
                self.are_any_failed_tests = False
                self.check_output_for_other_fails_or_errors_and_get_test_end_status()
            else:
                return job_status


    def _is_queued_or_running(self, only_once=None):
        if only_once:
            try:
                return self.jenkins_info['job_handler'].is_queued_or_running()
            except:
                self.failureStatus = 124
                self.test_end_status = "JenkinsError"
                logger.error('{} : {}'.format(self.jenkins_info['job_name'],LOGGER_INFO[self.failureStatus]))
                self.finish_with_failure()
        try:
            while True:
                if self.jenkins_info['job_handler'].is_queued_or_running():
                    time.sleep(3)       #TODO LONGER SLEEP LATER
                else:   break
        except:
            self.failureStatus = 124
            self.test_end_status = "JenkinsError"
            logger.error('{} : {}'.format(self.jenkins_info['job_name'],LOGGER_INFO[self.failureStatus]))
            self.finish_with_failure()


    def _build_job(self):
        try:
            self.jenkins_info['connection'].build_job(jobname=self.jenkins_info['job_name'],
                                                      params=self.jenkins_info['parameters'])
            logger.info("Job {} was built".format(self.jenkins_info['job_name']))
            return 0
        except:
            self.failureStatus = 107
            self.test_end_status = "JenkinsError"
            logger.error('{}'.format(LOGGER_INFO[self.failureStatus]))
            self.finish_with_failure()


    def set_jenkins_console_output(self):
        try:
            self._is_queued_or_running()
            self.jenkins_info['console_output'] = self.jenkins_info['job_handler'].get_last_build().get_console()
            logger.debug("Console output retrieved from {}".format(self.jenkins_info['job_name']))
            return self.jenkins_info['console_output']
        except:
            self.failureStatus = 108
            self.test_end_status = "JenkinsError"
            logger.error('{}'.format(LOGGER_INFO[self.failureStatus]))
            self.finish_with_failure()

    def parse_output_and_set_job_failed_tests(self):
        job_filenames_failed_tests=[]
        regex = r'\=\s(.*)\s\=\W*.*FAIL'
        try:
            matches = re.findall(regex, self.jenkins_info['console_output'])
            for match in matches:
                match = re.sub(" +", "_", match)  #changing " " to "_" - pybot thinks it's the same, i don't
                if match[-3:] == '...': match = match[:-3]  #cutting last "..."
                elif match[-1:] == '_': match = match[:-1]    #cutting last "_"
                try:
                    match = re.search('\w*\.Tests\.{}.*\.(.*)'.format(self.suitname), match).group(1)
                    job_filenames_failed_tests.append(match)
                except:
                    try:
                        match = re.search('\w*\.Tests\.(.*)', match).group(1)
                        job_filenames_failed_tests.append(match)
                    except:
                        match = re.search('\w*\.(.*)', match).group(1)
                        job_filenames_failed_tests.append(match)
        except:
            logger.debug("Regex did not find fails in output of {}".format(self.jenkins_info['job_name']))
        finally:
            if job_filenames_failed_tests:
                logger.info("Regex found fails in output of {}".format(self.jenkins_info['job_name']))
            self.job_filenames_failed_tests = job_filenames_failed_tests
            return self.job_filenames_failed_tests



    def check_for_fails(self):
        output = self.jenkins_info['console_output']
        if not output.find('| FAIL |') == -1:
            logger.debug("Found 'FAIL' in output of {}".format(self.jenkins_info['job_name']))
            return True
        output = output.split('\n')
        for line in output:
            if re.findall('\[.ERROR.\].*no tests.*', line):
                ###mozna zapisac, ze tag ciagle nie zmieniony i wysylac ponownie mail do testerow
                continue
            if not line.find('[ ERROR ]') == -1:
                logger.debug("Found 'ERROR' in output of {}".format(self.jenkins_info['job_name']))
                return True
        return False

    def check_output_for_other_fails_or_errors_and_get_test_end_status(self):
        if not self.are_any_failed_tests:
            if self.check_for_fails() == False:
                self.test_end_status = "SUCCESSFUL"
                logger.info("Test {} was successful".format(self.jenkins_info['job_name']))
            else:
                self.test_end_status = "UNKNOWN_ERROR/FAIL"
                self.are_any_failed_tests = True
                self.failureStatus = 109
                logger.error('{}'.format(LOGGER_INFO[self.failureStatus]))
                self.finish_with_failure()
        else:
            self.test_end_status = "GOT_FAILS"
            self.are_any_failed_tests = True
            logger.info("Test {} has got some failures".format(self.jenkins_info['job_name']))
        return self.test_end_status

    def get_SSHClient_connection(self):
        SSHClient = paramiko.SSHClient()
        SSHClient.load_system_host_keys()
        SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        SSHClient.connect(self.TLaddress, username='ute', password='ute')
        return SSHClient


    def check_if_more_directories(self):
        tmp_filenames_and_paths = []
        for root, dirs, files in os.walk('/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/{}'.format(self.suitname)):
            for file in files:
                if file.endswith('.robot') or file.endswith('.txt'):
                    tmp_filenames_and_paths.append({'path' : root, 'filename' : file})
        return tmp_filenames_and_paths


    def try_to_match_file_name(self, tmp_filenames_and_paths):
        filenames_and_paths = []
        for filename_from_output in self.job_filenames_failed_tests:
            _found = False
            for tmp_filename_and_path in tmp_filenames_and_paths:
                try:
                    re.search('({}.*)'.format(filename_from_output),tmp_filename_and_path['filename']).group(1)
                    filenames_and_paths.append({'path' : tmp_filename_and_path['path'], 'filename' : tmp_filename_and_path['filename']})
                    logger.debug("Found filename: {}".format(tmp_filename_and_path['filename']))
                    _found = True
                    break
                except:
                    pass
            if not _found:
                self.failureStatus = 110
                logger.warning('{} {}'.format(LOGGER_INFO[self.failureStatus],filename_from_output))

        return filenames_and_paths


    def remove_tag_from_robots_tests(self, old_tag = 'enable', new_tag = ''):
        tmp_filenames_and_paths = self.check_if_more_directories()
        filenames_and_paths = self.try_to_match_file_name(tmp_filenames_and_paths)

        for filename_and_path in filenames_and_paths:
            try:
                SSHClient = self.get_SSHClient_connection()
                file = SSHClient.open_sftp().open(os.path.join(filename_and_path['path'], filename_and_path['name']), 'r+')
                lines_in_file = file.readlines()
                file.seek(0)
                file.truncate()
                _found = False
                for line in lines_in_file:
                    try:
                        re.search('\[Tags](.*)', line).group(1)
                        try:
                            file.write(re.sub(old_tag, new_tag, line))
                            _found = True
                            logger.debug("Changed tag in file: {} from {} to {}".format(os.path.join(filename_and_path['path'], filename_and_path['name']), old_tag, new_tag))
                        except:
                            file.write(line)
                    except:
                        pass
                if not _found:
                    self.failureStatus = 111
                    self.test_end_status = "NO_TAG"
                    logger.warning('{} : {}'.format(LOGGER_INFO[self.failureStatus], old_tag))
            #   git_result = self.git_launch(file_info=[path, file_name])
            #   if not git_result == True:
            #         self.failureStatus = 114
            #         logger.warning('{} : {}'.format(LOGGER_INFO[self.failureStatus], git_result))
            #   logger.info("Git push successful on {}".format(self.TLname))

            except:
                self.failureStatus = 112
                self.test_end_status = "SSH_Connection_Failure"
                logger.warning('{}'.format(LOGGER_INFO[self.failureStatus]))
            finally:
                SSHClient.close()

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
