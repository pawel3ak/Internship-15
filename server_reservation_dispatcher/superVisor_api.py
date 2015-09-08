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
import json


from jenkinsapi.api import Jenkins
import ute_mail.sender
import ute_mail.mail
import paramiko

from utilities.TL_map import TL_map
from utilities.mailing_list import mail_dict, admin
from utilities.logger_messages import LOGGER_INFO
# from server_git_api import git_launch


# create logger
logger = logging.getLogger("server." + __name__)
#######################################################################################
# temporary
from utilities.logger_config import config_logger
config_logger(logger,'server_config.cfg')
########################################################################################

class SuperVisor(Jenkins):
    def __init__(self,TLname, jenkins_job_info, user_info):
        self.__jenkins_info = jenkins_job_info    #dict:{jobname : "", parameters : {param1 : "", ...}}
        self.__user_info = user_info          #dict:{first_name : "", last_name : "", mail :""}
        self.__TLname = TLname
        self.__suitname = jenkins_job_info['parameters']['name']
        super(SuperVisor, self).__init__('http://plkraaa-jenkins.emea.nsn-net.net:8080', username='nogiec', password='!salezjanierlz3!')
        self.__TLaddress = self.set_TLaddress_from_map()
        self.__failureStatus = None
        self.__are_any_failed_tests = False
        self.__test_end_status = None
        self.__filenames_of_failed_tests = None

        logger.debug("Created new Supervisor object with args: "
                     "jenkins_info = {}, user_info = {}, TLname = {}".format(self.__jenkins_info,
                                                                                      self.__user_info,
                                                                                      self.__TLname))

    #########################################################################################
    #getters and setters
    #########################################################################################

    def get_jenkins_info(self):
        return self.__jenkins_info


    def get_user_info(self):
        return self.__user_info


    def get_TLname(self):
        return self.__TLname


    def get_suitname(self):
        return self.__suitname


    def get_TLaddress(self):
        return self.__TLaddress


    def set_TLaddress_from_map(self):
        self.__TLaddress = TL_map[self.__TLname]
        return self.__TLaddress


    def get_failure_status(self):
        return self.__failureStatus


    def set_failure_status(self,status):
        self.__failureStatus = status


    def get_are_any_failed_tests(self):
        return self.__are_any_failed_tests


    def set_are_any_failed_tests(self, are_fails):
        self.__are_any_failed_tests = are_fails


    def get_test_end_status(self):
        return self.__test_end_status


    def set_test_end_status(self,status):
        self.__test_end_status = status


    def get_filenames_of_failed_tests(self):
        return self.__filenames_of_failed_tests


    def set_filenames_of_failed_tests(self, failed_tests):
        self.__filenames_of_failed_tests = failed_tests


    def get_job_parameters(self):
        return self.__jenkins_info['parameters']


    def set_default_jobname(self):
        self.__jenkins_info['jobname'] = 'test_on_{}'.format(self.get_TLname())


    def get_jobname(self):
        if 'jobname' in self.get_jenkins_info():
            return self.__jenkins_info['jobname']
        else:
            return None


    # def set_jenkins_connection(self):
    #     if not self.get_jobname():
    #         self.set_default_jobname()
    #     try:
    #         self.__jenkins_info['connection'] = Jenkins('http://plkraaa-jenkins.emea.nsn-net.net:8080', username='nogiec', password='!salezjanierlz3!')
    #         logger.debug("jenkins connection has been set")
    #     except:
    #         self.set_failure_status(106)
    #         self.set_test_end_status("JenkinsError")
    #         logger.critical('{}'.format(LOGGER_INFO[self.get_failure_status()]))
    #         self.finish_with_failure()


    # def get_jenkins_connection(self):
    #     return self.__jenkins_info['connection']


    def set_job_handler(self):
        try:
            self.__jenkins_info['job_handler'] = self.get_job(self.get_jobname())
        except:
            self.set_failure_status(125)
            self.set_test_end_status("JenkinsError")
            logger.critical('{}'.format(LOGGER_INFO[self.get_failure_status()]))
            self.finish_with_failure()


    def get_job_handler(self):
        return self.__jenkins_info['job_handler']


    def set_job_output(self, job_output):
        self.__jenkins_info['output'] = job_output


    def get_job_output(self):
        return self.__jenkins_info['output']


    def get_job_status(self):
        return self.__jenkins_info['job_status']


    #########################################################################################
    #functions
    #########################################################################################


    def make_file_with_specific_info(self):
        info_to_save = {
            'TLname'    : self.get_TLname(),
            'suitname'  : self.get_suitname(),
            'job_params': self.get_job_parameters()
        }
        path_with_filename = os.path.join('.','files','SuperVisor',self.get_suitname())
        with open(path_with_filename, 'wb') as file_with_specific_info:
            json.dump(info_to_save, file_with_specific_info)


    def delete_file_with_specific_info(self):
        path_with_filename = os.path.join('.','files','SuperVisor',self.get_suitname())
        for _ in range(10):
            try:
                os.remove(path_with_filename)
                break
            except:
                time.sleep(0.1)


    def finish_with_failure(self):
        self.send_information_about_executed_job()
        self.delete_file_with_specific_info()
        sys.exit()


    def set_node_for_job(self):
        try:
            job_config_xml = ET.fromstring(self.get_job_handler().get_config())
            assignedNode_tag = job_config_xml.find('assignedNode')
            assignedNode_tag.text = str(self.get_TLname())
            self.get_job_handler().update_config(ET.tostring(job_config_xml))
            logger.debug("Updated TL name: {} in job {}".format(self.get_TLname(), self.get_jobname()))
        except:
            self.set_failure_status(104)
            self.set_test_end_status("JenkinsError")
            logger.warning('{} : {}'.format(self.get_TLname(), LOGGER_INFO[self.get_failure_status()]))
            self.finish_with_failure()


    def set_job_status(self):
        try:
            self.__jenkins_info['job_status'] = self.get_job_handler().get_last_build().get_status()
        except:
            self.__jenkins_info['job_status'] = "UNKNOWN"
            self.set_failure_status(105)
            self.set_test_end_status("JenkinsError")
            logger.error('{} : {}'.format(self.get_jobname(),LOGGER_INFO[self.get_failure_status()]))
            self.finish_with_failure()
        finally:
            logger.debug("Job {} status = {}".format(self.get_jobname(), self.get_job_status()))


    def check_job_status(self):
        job_status = self.get_job_status()
        if job_status == "FAILURE":
            self.set_jenkins_console_output()
            self.set_are_any_failed_tests(False)
            self.check_output_for_other_fails_or_errors_and_set_test_end_status()
        elif job_status == "UNKNOWN":
            self.set_failure_status(127)
            self.set_test_end_status("JenkinsError")
            self.finish_with_failure()
        elif job_status == "SUCCESSFUL":
            pass


    def is_queued_or_running(self):
        try:
            while True:
                if self.get_job_handler().is_queued_or_running():
                    time.sleep(3)       #TODO LONGER SLEEP LATER
                else:   break
        except:
            self.set_failure_status(124)
            self.set_test_end_status("JenkinsError")
            logger.error('{} : {}'.format(self.get_jobname(),LOGGER_INFO[self.get_failure_status()]))
            self.finish_with_failure()


    def build_job(self):
        try:
            super(SuperVisor, self).build_job(jobname=self.get_jobname(),
                                                      params=self.get_job_parameters())
            logger.info("Job {} was built".format(self.get_jobname()))
        except:
            self.set_failure_status(107)
            self.set_test_end_status("JenkinsError")
            logger.error('{}'.format(LOGGER_INFO[self.get_failure_status()]))
            self.finish_with_failure()


    def set_jenkins_console_output(self):
        try:
            self.set_job_output(self.get_job_handler().get_last_build().get_console())
            logger.debug("Console output retrieved from {}".format(self.get_jobname()))
        except:
            self.set_failure_status(108)
            self.set_test_end_status("JenkinsError")
            logger.error('{}'.format(LOGGER_INFO[self.get_failure_status()]))
            self.finish_with_failure()


    def parse_output_and_set_job_failed_tests(self):
        job_filenames_failed_tests=[]
        # regex = r'\=\s(.*)\s\=\W*.*FAIL'
        regex = '*({}.*)\|.FAIL'.format(self.get_suitname())
        try:
            matches = re.findall(regex, self.get_job_output())
            self.set_are_any_failed_tests(True)
            for match in matches:
                match = re.sub(" +", "_", match)  #changing " " to "_" - pybot thinks it's the same, i don't
                if match[-3:] == '...': match = match[:-3]  #cutting last "..."
                elif match[-1:] == '_': match = match[:-1]    #cutting last "_"
                try:
                    match = re.search('\w*\.Tests\.{}.*\.(.*)'.format(self.get_suitname()), match).group(1)
                    job_filenames_failed_tests.append(match)
                except:
                    try:
                        match = re.search('\w*\.Tests\.(.*)', match).group(1)
                        job_filenames_failed_tests.append(match)
                    except:
                        try:
                            match = re.search('\w*\.(.*)', match).group(1)
                            job_filenames_failed_tests.append(match)
                        except:
                            pass
        except:
            logger.debug("Regex did not find fails in output of {}".format(self.get_jobname()))
        finally:
            if job_filenames_failed_tests:
                logger.info("Regex found fails in output of {}".format(self.get_jobname()))
            self.set_filenames_of_failed_tests(job_filenames_failed_tests)


    def check_for_fails(self):
        output = self.get_job_output()
        if not output.find('| FAIL |') == -1:
            logger.debug("Found 'FAIL' in output of {}".format(self.get_jobname()))
            return True
        output = output.split('\n')
        for line in output:
            if re.findall('\[.ERROR.\].*no tests.*', line):
                ###mozna zapisac, ze tag ciagle nie zmieniony i wysylac ponownie mail do testerow
                continue
            if not line.find('[ ERROR ]') == -1:
                logger.debug("Found 'ERROR' in output of {}".format(self.get_jobname()))
                return True
        return False


    # def write_tag_to_file_if_not_enabled(self):
    #     with open(os.path.join('.','files','SuperVisor','tests_without_tag.txt'), 'rb+') as test_without_tag_file:





    def check_output_for_other_fails_or_errors_and_set_test_end_status(self):
        if self.get_are_any_failed_tests() == False:
            if self.check_for_fails() == False:
                self.set_test_end_status("SUCCESSFUL")
                logger.info("Test {} was successful".format(self.get_jobname()))
            else:
                self.set_test_end_status("UNKNOWN_ERROR/FAIL")
                self.set_are_any_failed_tests(True)
                self.set_failure_status(109)
                logger.error('{}'.format(LOGGER_INFO[self.get_failure_status()]))
                self.finish_with_failure()
        else:
            self.set_test_end_status("GOT_FAILS")
            logger.info("Test {} has got some failures".format(self.get_jobname()))


    def __get_SSHClient_connection(self):
        try:
            SSHClient = paramiko.SSHClient()
            SSHClient.load_system_host_keys()
            SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            SSHClient.connect(self.get_TLaddress(), username='ute', password='ute')
            return SSHClient
        except:
            return None


    def __get_robot_files_and_paths(self):
        tmp_filenames_and_paths = []
        for root, dirs, files in os.walk('/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/{}'.format(self.__suitname)):
            for file in files:
                if file.endswith('.robot') or file.endswith('.txt'):
                    tmp_filenames_and_paths.append({'path' : root, 'filename' : file})
        return tmp_filenames_and_paths


    def __match_filenames_and_paths(self, tmp_filenames_and_paths):
        filenames_and_paths = []
        filenames_and_paths_for_temporary_use = []
        for filename_from_output in self.get_filenames_of_failed_tests():
            _found = False
            for tmp_filename_and_path in tmp_filenames_and_paths:
                try:
                    re.search('({}.*)'.format(filename_from_output),tmp_filename_and_path['filename']).group(1)
                    filenames_and_paths.append({'path' : tmp_filename_and_path['path'], 'filename' : tmp_filename_and_path['filename']})
                    filenames_and_paths_for_temporary_use.append(tmp_filename_and_path['filename'])
                    logger.debug("Found filename: {}".format(tmp_filename_and_path['filename']))
                    _found = True
                    break
                except:
                    pass
            if not _found:
                filenames_and_paths_for_temporary_use.append(filename_from_output)
                self.set_failure_status(110)
                logger.warning('{} {}'.format(LOGGER_INFO[self.get_failure_status()],filename_from_output))
        self.set_filenames_of_failed_tests(filenames_and_paths_for_temporary_use)
        return filenames_and_paths


    def remove_tag_from_robots_tests(self, old_tag = 'enable', new_tag = ''):
        tmp_filenames_and_paths = self.__get_robot_files_and_paths()
        filenames_and_paths = self.__match_filenames_and_paths(tmp_filenames_and_paths)
        SSHClient = None
        try:
            SSHClient = self.__get_SSHClient_connection()
        except:
            self.set_failure_status(128)
            logger.warning('{}'.format(self.get_failure_status()))
            self.set_test_end_status("SSH_Connection_Failure")
            self.finish_with_failure()
        __found = False
        for filename_and_path in filenames_and_paths:
            try:
                SFTP = SSHClient.open_sftp()
                file = SFTP.file(os.path.join(filename_and_path['path'], filename_and_path['filename']), 'r')
                lines_in_file = file.readlines()
                for line in lines_in_file:
                    try:
                        re.search('.*\[Tags](.*)', line).group(1)
                        try:
                            lines_in_file[lines_in_file.index(line)] = re.sub(old_tag, new_tag, line)
                            __found = True
                            logger.debug("Changed tag in file: {} from {} to {}".format(os.path.join(filename_and_path['path'], filename_and_path['name']), old_tag, new_tag))
                        except:
                            self.set_failure_status(129)
                            logger.warning('"{}" {}'.format(old_tag, LOGGER_INFO[self.get_failure_status()]))
                    except:
                        pass
                file.close()
                file2 = SFTP.file(os.path.join(filename_and_path['path'], filename_and_path['filename']), 'w')
                file2.writelines(lines_in_file)
                file2.close()
                SSHClient.close()

            #   git_result = self.git_launch(file_info=[path, file_name])
            #   if not git_result == True:
            #         self.failureStatus = 114
            #         logger.warning('{} : {}'.format(LOGGER_INFO[self.failureStatus], git_result))
            #   logger.info("Git push successful on {}".format(self.TLname))

            except:
                self.set_failure_status(112)
                self.set_test_end_status("SSH_Connection_Failure")
                logger.warning('{}'.format(LOGGER_INFO[self.get_failure_status()]))
            finally:
                SSHClient.close()
        if not __found:
            self.set_failure_status(111)
            self.set_test_end_status("NO_TAG")
            logger.warning('{} : {}'.format(LOGGER_INFO[self.get_failure_status()], old_tag))


    def send_information_about_executed_job(self):
        test_end_status = self.get_test_end_status()
        messages = []

        if test_end_status == "PASS":
            return 0

        elif test_end_status == "GOT_FAILS":
            t = self.get_job_handler().get_last_build().get_timestamp()
            build_time = '{}-{:02g}-{:02g}_{:02g}-{:02g}-{:02g}'.format(t.year, t.month, t.day, (t.hour-(time.altzone/3600)), t.minute, t.second)
            logs_url_address = 'http://10.83.200.35/~ltebox/logs/{}_{}/log.html'.format(self.__TLname, build_time)
            failed_tests_information = ''

            for filename in self.get_filenames_of_failed_tests():
                failed_tests_information += "{test_name}.{filename}\n".format(
                    test_name=self.get_suitname(),
                    filename=filename)
            _message = "Dear tester! \n\n" \
                        "Your test have failed: \n\n" \
                        "{test_info}\n\n" \
                        "Logs are available at: {logs_link}\n\n" \
                        "Have a nice day!".format(test_info=failed_tests_information,
                                                  logs_link=logs_url_address)
            messages.append({'message' : _message,
                            'feature' : self.get_suitname()})
            subject = "Tests status update - finished with fail"


        elif test_end_status == 'UNKNOWN_ERROR/FAIL':
            logs_url_address = '{url}/job/{job_name}/{bn}/console'.format(url= 'http://plkraaa-jenkins.emea.nsn-net.net:8080',
                                                                  job_name=self.get_jobname(),
                                                                  bn=self.get_job_handler().get_last_buildnumber())
            _message = "Dear Admin! \n\n" \
                       "Tests on {tl_name} occured unknown fail.\n" \
                       "Please check logs available at: {logs_link} \n\n" \
                       "Have a nice day!".format(tl_name=self.get_TLname(),
                                                 logs_link=logs_url_address)
            messages.append({'message' : _message})
            subject = "Tests status update - finished with unknown fail"

        elif test_end_status == 'JenkinsError':
            _message = "Dear Admin! \n\n" \
                       "There is some problems with Jenkins. Please check it.\n\n" \
                       "Have a nice day!"
            messages.append({'message' : _message})
            subject = "Tests status update - JenkinsError"

        elif test_end_status == 'SSH_Connection_Failure':
            _message = "Dear Admin! \n\n" \
                       "There is some problems with SSH connection to Belvedere. Please check it.\n\n" \
                       "Have a nice day!"
            messages.append({'message' : _message})
            subject = "Tests status update - SSHError"

        elif test_end_status == 'NO_TAG':
            _message = "Dear Admin! \n\n" \
                       "I couldn't find TAG in files from testsuite '{}'. Please check it.\n\n" \
                       "Have a nice day!".format(self.get_suitname())
            messages.append({'message' : _message})
            subject = "Tests status update - JenkinsError"

        if 'feature' in messages[0]:
            for message in messages:
                mail = ute_mail.mail.Mail(subject=subject,message=message['message'],
                                          recipients=mail_dict[message['feature']],
                                          name_from="Reservation Api")
                send = ute_mail.sender.SMTPMailSender(host = '10.150.129.55')
                send.connect()
                send.send(mail)

        else:
            mail = ute_mail.mail.Mail(subject=subject,message=messages[0]['message'],
                                          recipients=admin['mail'],  #Bartek Kukla (?) mail here
                                          name_from="Reservation Api")          #We need to figure out better name
            send = ute_mail.sender.SMTPMailSender(host = '10.150.129.55')
            send.connect()
            send.send(mail)

    # def git_launch(self, file_info=None, pull_only=None):
    #     return git_launch(TL_address=self.TLaddress, file_info=file_info, pull_only=pull_only)
