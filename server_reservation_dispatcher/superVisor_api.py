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
from urllib import urlencode

from jenkinsapi.api import Jenkins
from jenkinsapi.node import Node
import ute_mail.sender
import ute_mail.mail
import paramiko

from utilities.mailing_list import mail_dict, admin
from utilities.logger_messages import logging_messages
from ours_git_api import perform_git_basic_command_to_update_repo

logger = logging.getLogger("server." + __name__)
logger.setLevel(logging.DEBUG)
#######################################################################################
# temporary
# from utilities.logger_config import config_logger
# config_logger(logger,'server_config.cfg')
########################################################################################

class SuperVisor(Jenkins):
    def __init__(self, TLname, jenkins_job_info, user_info):
        self.__jenkins_info = jenkins_job_info  # dict:{jobname : "", parameters : {param1 : "", ...}}
        self.__user_info = user_info  # dict:{first_name : "", last_name : "", mail :""}
        self.__TLname = TLname
        self.__suitname = jenkins_job_info['parameters']['name']
        self.logger_adapter = logging.LoggerAdapter(logger, {'custom_name': self.__suitname})
        self.TL_name_to_address_map_path = os.path.join('.', 'utilities', 'TL_name_to_address_map.data')  #full path after copy to belvedere
        self.file_with_basic_info_path = os.path.join('.', 'files', 'SuperVisor', self.get_suitname())
        self.testsWithoutTag_file_path = os.path.join('.', 'files', 'SuperVisor', 'testsWithoutTag.txt')
        self.suitename_folder_path = os.path.join('/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN', self.get_suitname())
        self.__TLaddress = self.set_TLaddress_from_map()
        self.__are_any_failed_tests = False
        self.__test_end_status = None
        self.__filenames_of_failed_tests = None
        self.__commit_version = None

        try:
            super(SuperVisor, self).__init__('http://plkraaa-jenkins.emea.nsn-net.net:8080', username='crt', password='Flexi1234')
            self.set_default_jobname()
            self.create_node_if_not_exists()
        except:
            self.set_test_end_status("JenkinsError")
            self.logger_adapter.critical('{}'.format(logging_messages(124)))
            self.finish_with_failure()

        self.logger_adapter.debug(logging_messages(100,
                                                      jenkins=self.get_jenkins_info(),
                                                      user_info=self.get_user_info(),
                                                      TLname=self.get_TLname()))
        self.set_commit_version(self.get_last_commit_from_file())

        perform_git_basic_command_to_update_repo(self.get_TLaddress(), self.suitename_folder_path, pull_only=True)

    def __exit__(self):
        self.delete_file_with_basic_info()
        self.delete_node(self.get_TLname())

    #########################################################################################
    # getters and setters
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
        if not os.path.exists(self.TL_name_to_address_map_path):
            self.logger_adapter.critical(logging_messages(135, TLname=self.get_TLname()))
            self.set_test_end_status("No_TLaddress")
            self.finish_with_failure()
        else:
            with open(self.TL_name_to_address_map_path, "rb") as TL_map_file:
                TL_map = [json.loads(line.strip()) for line in TL_map_file.readlines()]
                try:
                    TLaddress = [address[self.get_TLname()] for address in TL_map if self.get_TLname() in address][0]
                    return TLaddress
                except:
                    self.logger_adapter.critical(logging_messages(135, TLname=self.get_TLname()))
                    self.set_test_end_status("No_TLaddress")
                    self.finish_with_failure()

    def get_are_any_failed_tests(self):
        return self.__are_any_failed_tests

    def set_are_any_failed_tests(self, are_fails):
        self.__are_any_failed_tests = are_fails

    def get_test_end_status(self):
        return self.__test_end_status

    def set_test_end_status(self, status):
        self.__test_end_status = status

    def get_filenames_of_failed_tests(self):
        return self.__filenames_of_failed_tests

    def set_filenames_of_failed_tests(self, failed_tests):
        self.__filenames_of_failed_tests = failed_tests

    def get_commit_version(self):
        return self.__commit_version

    def set_commit_version(self, version):
        self.__commit_version = version

    def get_job_parameters(self):
        return self.__jenkins_info['parameters']

    def set_default_jobname(self):
        self.__jenkins_info['jobname'] = 'dispatcher_{}'.format(self.get_TLname())

    def get_jobname(self):
        if 'jobname' in self.get_jenkins_info():
            return self.__jenkins_info['jobname']
        else:
            return None

    def create_node_if_not_exists(self):
        if not self.has_node(self.get_TLname()):
            print "Tworze node"
            self.create_node(self.get_TLname())

    def create_node(self, name, num_executors=2, node_description=None,
                    remote_fs='/home/ute', labels=None, exclusive=False):
        """
        Create a new slave node by name.

        :param name: fqdn of slave, str
        :param num_executors: number of executors, int
        :param node_description: a freetext field describing the node
        :param remote_fs: jenkins path, str
        :param labels: labels to associate with slave, str
        :param exclusive: tied to specific job, boolean
        :return: node obj
        """
        NODE_TYPE = 'hudson.slaves.DumbSlave$DescriptorImpl'
        MODE = 'NORMAL'
        # if self.has_node(name):
        #     return Node(nodename=name, baseurl=self.get_node_url(nodename=name), jenkins_obj=self)
        if exclusive:
            MODE = 'EXCLUSIVE'
        params = {
            'name': name,
            'type': NODE_TYPE,
            'json': json.dumps({
            'name': name,
            'nodeDescription': node_description,
            'numExecutors': num_executors,
            'remoteFS': remote_fs,
            'labelString': labels,
            'mode': MODE,
            'type': NODE_TYPE,
            'retentionStrategy': {'stapler-class': 'hudson.slaves.RetentionStrategy$Always'},
            'nodeProperties': {'stapler-class-bag': 'true'},
            'launcher': {'stapler-class': 'hudson.plugins.sshslaves.SSHLauncher',
                         "host": self.get_TLaddress(),
                         "port": "22",
                         "username" : "ute",
                         "password": "ute2"}
            })
        }
        url = self.get_node_url() + "doCreateItem?%s" % urlencode(params)
        self.requester.get_and_confirm_status(url)
        return Node(nodename=name, baseurl=self.get_node_url(nodename=name), jenkins_obj=self)

    def get_jenkins_connection(self):
        return self
        # return self.__jenkins_info['connection']

    def set_job(self):
        try:
            self.job = self.get_job(self.get_jobname())
        except:
            self.set_test_end_status("JenkinsError")
            self.logger_adapter.critical(logging_messages(125, jobname=self.get_jobname()))
            self.finish_with_failure()

    def get_job_output(self):
        return self.job.get_last_build().get_console()
        # return self.__jenkins_info['output']

    def get_job_status(self):
        for _ in range(5):
            try:
                return self.job.get_last_build().get_status()
            except:
                pass
        self.set_test_end_status("JenkinsError")
        self.logger_adapter.critical(logging_messages(135, jobname=self.get_jobname()))
        self.finish_with_failure()
        # return self.__jenkins_info['job_status']

    def make_file_with_basic_info(self):
        """
        creates file with basic informations about this specific supervisor object
        :return: nothing
        """
        info_to_save = {
            'TLname': self.get_TLname(),
            'suitname': self.get_suitname(),
            'job_params': self.get_job_parameters()
        }
        with open(self.file_with_basic_info_path, 'wb') as file_with_basic_info:
            json.dump(info_to_save, file_with_basic_info)

    def delete_file_with_basic_info(self):
        if not os.path.exists(self.file_with_basic_info_path):
            return
        else:
            for _ in range(5):
                try:
                    os.remove(self.file_with_basic_info_path)
                    break
                except:
                    time.sleep(0.2)

    def finish_with_failure(self):
        self.send_information_about_executed_job()
        self.delete_file_with_basic_info()
        self.logger_adapter.critical(logging_messages(130, test_end_status=self.get_test_end_status()))
        sys.exit(1)

    def set_node_for_job(self):
        try:
            job_config_xml = ET.fromstring(self.job.get_config())
            assignedNode_tag = job_config_xml.find('assignedNode')
            assignedNode_tag.text = str(self.get_TLname())
            self.job.update_config(ET.tostring(job_config_xml))
            self.logger_adapter.debug(logging_messages(116, TLname=self.get_TLname(), jobname=self.get_jobname()))
        except:
            self.set_test_end_status("JenkinsError")
            self.logger_adapter.critical(logging_messages(104, TLname=self.get_TLname(), jobname=self.get_jobname()))
            self.finish_with_failure()

    def check_job_status(self):
        job_status = self.get_job_status()
        if job_status == "FAILURE":
            # self.set_jenkins_console_output()
            self.set_are_any_failed_tests(False)
            self.check_output_for_other_fails_or_errors_and_set_test_end_status()
        elif job_status == "SUCCESS":
            pass
        else:
            self.set_test_end_status("JenkinsError")
            self.logger_adapter.critical(logging_messages(135, jobname=self.get_jobname()))
            self.finish_with_failure()

    def is_queued_or_running(self, once=False):
        try:
            while not once:
                if self.job.is_queued_or_running():
                    time.sleep(3)  # TODO LONGER SLEEP LATER
                else:
                    return False
            return self.job.is_queued_or_running()
        except:
            self.set_test_end_status("JenkinsError")
            self.logger_adapter.critical(logging_messages(124, jobname=self.get_jobname()))
            self.finish_with_failure()

    def build_job(self):
        try:
            super(SuperVisor, self).build_job(jobname=self.get_jobname(),
                                              params=self.get_job_parameters())
            self.logger_adapter.info(logging_messages(118, jobname=self.get_jobname()))
        except:
            self.set_test_end_status("JenkinsError")
            self.logger_adapter.critical(logging_messages(107, jobname=self.get_jobname()))
            self.finish_with_failure()

    @staticmethod
    def check_job_output_for_filenames(match, regex):
        job_filenames_failed_tests = []
        try:
            job_filenames_failed_tests.append(re.search(regex, match).group(1))
        except:
            pass
        finally:
            if job_filenames_failed_tests:
                return job_filenames_failed_tests

    def findall_test_failes(self):
        regex = r'({}.*)\s\=\W*.*FAIL'.format(self.get_suitname())
        matches = re.findall(regex, self.get_job_output())
        if matches:
            self.set_are_any_failed_tests(True)
        return matches

    @staticmethod
    def prepare_output_for_regex_matching(match):
        match = re.sub(" +", "_", match)  # changing " " to "_" - pybot thinks it's the same, i don't
        if match[-3:] == '...': match = match[:-3]  # cutting last "..."
        elif match[-1:] == '_': match = match[:-1]  # cutting last "_"
        return match

    def parse_output_and_set_job_failed_tests(self):
        job_filenames_failed_tests = []
        try:
            matches = self.findall_test_failes()
            for match in matches:
                match = self.prepare_output_for_regex_matching(match)
                regexps = ['\w*\.Tests\.{}.*\.({}.*)'.format(self.get_suitname(), self.get_suitname()),
                           '\w*\.Tests\.({}.*)'.format(self.get_suitname()),
                           '\w*\.({}.*)'.format(self.get_suitname())]
                try:
                    job_filenames_failed_tests = [self.check_job_output_for_filenames(match, regex)
                                                  for regex in regexps if self.check_job_output_for_filenames(match, regex)][0]
                    self.logger_adapter.info(logging_messages(10, word='found', jobname=self.get_jobname()))
                    self.set_test_end_status("GOT_FAILS")
                except:
                    pass
        except:
            self.logger_adapter.debug(logging_messages(10, word='did not find', jobname=self.get_jobname()))
        finally:
            self.set_filenames_of_failed_tests(job_filenames_failed_tests)
            self.check_output_for_other_fails_or_errors_and_set_test_end_status()

    def check_output_for_fails(self):
        output = self.get_job_output()
        if not output.find('| FAIL |') == -1:
            self.logger_adapter.debug(logging_messages(11, jobname=self.get_jobname()))
            return True
        return False

    def check_output_for_errors(self):
        output = self.get_job_output().split('\n')
        for line in output:
            if re.findall('\[.ERROR.\].*no tests.*', line):
                self.write_suitename_to_testsWithoutTag_file_if_no_enable_tag_in_suite()
                continue
            if not line.find('[ ERROR ]') == -1:
                self.logger_adapter.debug(logging_messages(13, jobname=self.get_jobname()))
                return True
        return False

    def check_output_for_other_fails_or_errors_and_set_test_end_status(self):
        if not self.get_are_any_failed_tests():
            if not self.check_output_for_fails() and not self.check_output_for_errors():
                self.set_test_end_status("SUCCESSFUL")
                self.logger_adapter.debug(logging_messages(131, suitename=self.get_suitname()))
            else:
                self.set_are_any_failed_tests(True)
                self.finish_with_failure()

    @staticmethod
    def check_if_file_exists_and_create_if_not(path):
        if not os.path.exists(path):
            os.mknod(path)

    @staticmethod
    def clear_file(fd):
        fd.seek(0)
        fd.truncate()

    def remove_tag_from_testsWithoutTag_file_if_tag_is_in_suite(self):
        self.check_if_file_exists_and_create_if_not(self.testsWithoutTag_file_path)
        with open(self.testsWithoutTag_file_path, 'rb+') as testWithoutTag_file:
            lines_in_file = [line_in_file for line_in_file in testWithoutTag_file.readlines()
                             if not line_in_file.strip() == '' and self.get_suitname() not in line_in_file]
            self.clear_file(testWithoutTag_file)
            [testWithoutTag_file.writelines(line_in_file) for line_in_file in lines_in_file]
            self.logger_adapter.info(logging_messages(12, suitename=self.get_suitname()))

    def write_suitename_to_testsWithoutTag_file_if_no_enable_tag_in_suite(self):
        self.check_if_file_exists_and_create_if_not(self.testsWithoutTag_file_path)
        with open(self.testsWithoutTag_file_path, 'rb+') as testsWithoutTag_file:
            lines_in_file = [json.loads(line) for line in testsWithoutTag_file.readlines() if not line.strip() == '']
            try:
                index = (lines_in_file.index(line) for line in lines_in_file if self.get_suitname() in line).next()
                lines_in_file[index][self.get_suitname()] += 1
                self.logger_adapter.info(logging_messages(119, suitename=self.get_suitname()))
            except:
                lines_in_file.append({self.get_suitname(): 1})
                self.logger_adapter.info(logging_messages(119, suitename=self.get_suitname()))
            self.clear_file(testsWithoutTag_file)
            [testsWithoutTag_file.writelines('{}\n'.format(json.dumps(line))) for line in lines_in_file]

    def get_SSHClient_connection(self):
        for _ in range(5):
            try:
                SSHClient = paramiko.SSHClient()
                SSHClient.load_system_host_keys()
                SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                SSHClient.connect(self.get_TLaddress(), username='ute', password='ute')
                return SSHClient
            except:
                pass
        return None

    def __get_robot_filenames_and_paths(self):
        tmp_filenames_and_paths = []
        for root_path, directories, filenames in os.walk(self.suitename_folder_path):
            [tmp_filenames_and_paths.append({'path': root_path, 'filename': filename})
             for filename in filenames if filename.endswith('.robot') or filename.endswith('.txt')]
        return tmp_filenames_and_paths

    def __match_filenames_and_paths(self, tmp_filenames_and_paths):
        filenames_and_paths = []
        for filename_from_output in self.get_filenames_of_failed_tests():
            matches = [(re.search('({}.*)'.format(filename_from_output), tmp_filename_and_path['filename']),
                        tmp_filename_and_path['path']) for tmp_filename_and_path in tmp_filenames_and_paths]
            [filenames_and_paths.append({'filename': match[0].group(1), 'path': match[1]}) for match in matches if match[0]]
        self.set_filenames_of_failed_tests([tmp_filename_and_path['filename'] for tmp_filename_and_path in tmp_filenames_and_paths])
        return filenames_and_paths

    def remove_tag_from_robots_tests(self, old_tag='enable', new_tag=''):
        tmp_filenames_and_paths = self.__get_robot_filenames_and_paths()
        filenames_and_paths = self.__match_filenames_and_paths(tmp_filenames_and_paths)
        SSHClient = self.get_SSHClient_connection()
        if not SSHClient:
            self.logger_adapter.warning(logging_messages(128))
            self.set_test_end_status("SSH_Connection_Failure")
            self.finish_with_failure()
        for filename_and_path in filenames_and_paths:
            robot_file_path = os.path.join(filename_and_path['path'], filename_and_path['filename'])
            try:
                SFTP = SSHClient.open_sftp()
                robot_file = SFTP.file(robot_file_path, 'r')
                lines_in_robot_file = robot_file.readlines()
                matches = [re.search('(.*\[Tags].*)', line) for line in lines_in_robot_file]
                try:
                    match, index = ((match.group(1), matches.index(match)) for match in matches if match).next()
                    lines_in_robot_file[index] = re.sub(old_tag, new_tag, match)
                    self.logger_adapter.debug(logging_messages(132, filename=robot_file_path, old_tag=old_tag, new_tag=new_tag))
                except:
                    self.logger_adapter.warning(logging_messages(129, old_tag=old_tag))
                robot_file.close()
                file2 = SFTP.file(os.path.join(filename_and_path['path'], filename_and_path['filename']), 'w')
                file2.writelines(lines_in_robot_file)
                file2.close()
                # TODO Git on appropiate TL
            #   git_result = self.perform_git_basic_command_to_update_repo(file_info=[path, file_name])
            #   if not git_result == True:
            #         self.failureStatus = 114
            #         self.logger_adapter.warning('{} : {}'.format(LOGGER_INFO[self.failureStatus], git_result))
            #   self.logger_adapter.info("Git push successful on {}".format(self.TLname))

            except:
                self.logger_adapter.warning(logging_messages(112, robot_file_path))
            finally:
                SSHClient.close()

    def get_last_commit_from_file(self):
        SSHClient = self.get_SSHClient_connection()
        if not SSHClient:
            self.logger_adapter.warning(logging_messages(133))
        else:
            try:
                SFTP = SSHClient.open_sftp()
                file_with_last_commit = SFTP.file("/home/ute/auto/ruff_scripts/.git/FETCH_HEAD", "r")
                last_commit = file_with_last_commit.read().split()[0]
                return last_commit
            except:
                self.logger_adapter.warning(logging_messages(134))

    def get_logs_link(self):
        if self.get_job_status() == "SUCCESS":
            t = self.job.get_last_build().get_timestamp()
            build_time = '{}-{:02g}-{:02g}_{:02g}-{:02g}-{:02g}'.format(t.year, t.month, t.day, (t.hour-(time.altzone/3600)), t.minute, t.second)
            logs_url_address = 'http://10.83.200.35/~ltebox/logs/{}_{}/log.html'.format(self.__TLname, build_time)
        else:
            logs_url_address = '{url}/job/{job_name}/{bn}/console'.format(url='http://plkraaa-jenkins.emea.nsn-net.net:8080',
                                                                          job_name=self.get_jobname(),
                                                                          bn=self.job.get_last_buildnumber())
        return logs_url_address

    def choose_recipient_name(self):
        if self.get_user_info():
            recipient_name = "{} {}".format(self.get_user_info()['first_name'],
                                            self.get_user_info()['last_name'])
        else:
            if self.get_test_end_status() == "GOT_FAIL" or self.get_test_end_status() == "Tester slacking":
                recipient_name = "Tester"
            else:
                recipient_name = "Admin"
        return recipient_name

    def set_mail_message_and_subject(self):
        test_end_status = self.get_test_end_status()
        messages = []
        subject = ""

        if not test_end_status:
            test_end_status="NOT_CAUGHT_ERROR/FAIL"

        if test_end_status == "SUCCESSFUL":
            if self.get_user_info():
                _message = "Dear {}!\n\n" \
                           "Your test '{}' status is {}\n" \
                           "Logs are available at {}\n\n" \
                           "Have a nice day!".format(self.choose_recipient_name(),
                                                     self.get_suitname(),
                                                     self.get_job_status(),
                                                     self.get_logs_link())
                messages.append({'message': _message})
                subject = "Test status update"
            else:
                return 0, 0

        elif test_end_status == "GOT_FAILS":
            t = self.job.get_last_build().get_timestamp()
            build_time = '{}-{:02g}-{:02g}_{:02g}-{:02g}-{:02g}'.format(t.year, t.month, t.day, (t.hour-(time.altzone/3600)), t.minute, t.second)
            logs_url_address = 'http://10.83.200.35/~ltebox/logs/{}_{}/log.html'.format(self.__TLname, build_time)
            failed_tests_information = ''

            for filename in self.get_filenames_of_failed_tests():
                failed_tests_information += "{test_name}.{filename}\n".format(
                    test_name=self.get_suitname(),
                    filename=filename)
            _message = "Dear {}! \n\n" \
                       "Your test have failed: \n\n" \
                       "{test_info}\n\n" \
                       "Git version = {commit_version}\n\n" \
                       "Logs are available at: {logs_link}\n\n" \
                       "Have a nice day!".format(self.choose_recipient_name(),
                                                 test_info=failed_tests_information,
                                                 commit_version=self.get_commit_version(),
                                                 logs_link=logs_url_address)
            messages.append({'message': _message,
                             'feature': self.get_suitname()})
            subject = "Tests status update - finished with fail"

        elif test_end_status == 'NOT_CAUGHT_ERROR/FAIL':
            logs_url_address = '{url}/job/{job_name}/{bn}/console'.format(url='http://plkraaa-jenkins.emea.nsn-net.net:8080',
                                                                          job_name=self.get_jobname(),
                                                                          bn=self.job.get_last_buildnumber())
            _message = "Dear {}! \n\n" \
                       "Tests on {tl_name} occured unknown fail.\n" \
                       "Please check logs available at: {logs_link} \n\n" \
                       "Have a nice day!".format(self.choose_recipient_name(),
                                                 tl_name=self.get_TLname(),
                                                 logs_link=logs_url_address)
            messages.append({'message': _message})
            subject = "Tests status update - finished with unknown fail"

        elif test_end_status == 'JenkinsError':
            _message = "Dear {}! \n\n" \
                       "There is some problems with Jenkins. Please check it.\n\n" \
                       "Have a nice day!".format(self.choose_recipient_name())
            messages.append({'message': _message})
            subject = "Tests status update - JenkinsError"

        elif test_end_status == 'SSH_Connection_Failure':
            _message = "Dear {}! \n\n" \
                       "There is some problems with SSH connection to Belvedere. Please check it.\n\n" \
                       "Have a nice day!".format(self.choose_recipient_name())
            messages.append({'message': _message})
            subject = "Tests status update - SSHError"

        elif test_end_status == 'Tester slacking':
            _message = "Dear {}! \n\n" \
                       "You still didn't checked your test!\n" \
                       "Testsuite = '{}'. Please check it.\n\n" \
                       "Have a nice day!".format(self.choose_recipient_name(),
                                                 self.get_suitname())
            messages.append({'message': _message,
                             'feature': self.get_suitname()})
            subject = "Tests status update - You are slacking"
        print "test end status = {}\nsubject = {}\n".format(test_end_status, subject)
        return messages, subject

    def send_information_about_executed_job(self):
        (messages, subject) = self.set_mail_message_and_subject()
        if messages == 0 and subject == 0:
            return 0
        if self.get_user_info():
            recipients = self.get_user_info()['mail']
        else:
            print self.get_suitname()
            print messages
            if 'feature' in messages[0]:
                try:
                    recipients = mail_dict[messages[0]['feature']]
                except:
                    recipients = admin['mail']
            else:
                recipients = admin['mail']

        mail = ute_mail.mail.Mail(subject=subject, message=messages[0]['message'],
                                  recipients=recipients,
                                  name_from="Reservation Api")
        send = ute_mail.sender.SMTPMailSender(host='10.150.129.55')
        send.connect()
        send.send(mail)
