# -*- coding: utf-8 -*-
"""
:created on: '11/08/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nokia.com
"""
from audiodev import test
from distutils.log import Log

import time
import xml.etree.ElementTree as ET
import re
import os
import sys
import logging
import json
from celery.worker import job

from jenkinsapi.api import Jenkins
import ute_mail.sender
import ute_mail.mail
import paramiko

from utilities.mailing_list import mail_dict, admin
from utilities.logger_messages import LOGGER_INFO
# from server_git_api import git_launch


# create logger
logger = logging.getLogger("server." + __name__)
#######################################################################################
# temporary

from utilities.logger_config import config_logger
logger.setLevel(logging.DEBUG)
config_logger(logger,'server_config.cfg')

########################################################################################

class SuperVisor(Jenkins):
    def __init__(self,TLname, jenkins_job_info, user_info):
        self.__jenkins_info = jenkins_job_info    #dict:{jobname : "", parameters : {param1 : "", ...}}
        self.__user_info = user_info          #dict:{first_name : "", last_name : "", mail :""}
        self.__TLname = TLname
        self.__suitname = jenkins_job_info['parameters']['name']
        self.TL_name_to_address_map_path = os.path.join('.','utilities','TL_name_to_address_map.data') #full path after copy to belvedere
        self.file_with_basic_info_path = os.path.join('.', 'files', 'SuperVisor', self.get_suitname())
        self.testsWithoutTag_file_path = os.path.join('.', 'files', 'SuperVisor', 'testsWithoutTag.txt')
        self.suitename_folder_path = os.path.join('/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN', self.get_suitname())
        self.__TLaddress = self.set_TLaddress_from_map()
        self.__are_any_failed_tests = False
        self.__test_end_status = None
        self.__filenames_of_failed_tests = None

        try:
            super(SuperVisor, self).__init__('http://plkraaa-jenkins.emea.nsn-net.net:8080', username='nogiec', password='!salezjanierlz3!')
        except:
            self.set_test_end_status("JenkinsError")
            logger.critical('{}'.format(LOGGER_INFO[124]))
            self.finish_with_failure()


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
        if not os.path.exists(self.TL_name_to_address_map_path):
            logger.critical("Cannot get TL address!")
            self.set_test_end_status("No_TLaddress")
            self.finish_with_failure()
        else:
            with open(self.TL_name_to_address_map_path, "rb") as TL_map_file:
                TL_map = [json.loads(line.strip()) for line in TL_map_file.readlines()]
                try:
                    TLaddress = [address[self.get_TLname()] for address in TL_map if self.get_TLname() in address][0]
                    return TLaddress
                except:
                    logger.critical("Cannot get TL address!")
                    self.set_test_end_status("No_TLaddress")
                    self.finish_with_failure()


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


    def get_job_build_number(self):
        return self.__jenkins_info['build_number']


    def set_job_build_number(self, build_number):
        self.__jenkins_info['build_number'] = build_number


    def get_jobname(self):
        if 'jobname' in self.get_jenkins_info():
            return self.__jenkins_info['jobname']
        else:
            return None


    def set_jenkins_connection(self):
        if not self.get_jobname():
            self.set_default_jobname()
        try:
            self.__jenkins_info['connection'] = Jenkins('http://plkraaa-jenkins.emea.nsn-net.net:8080', username='nogiec', password='!salezjanierlz3!')
            logger.debug("jenkins connection has been set")
        except:
            self.set_test_end_status("JenkinsError")
            logger.critical('{}'.format(LOGGER_INFO[106]))
            self.finish_with_failure()


    def get_jenkins_connection(self):
        return self.__jenkins_info['connection']


    def set_job_handler(self):
        try:
            self.__jenkins_info['job_handler'] = self.get_job(self.get_jobname())
        except:
            self.set_test_end_status("JenkinsError")
            logger.critical('{}'.format(LOGGER_INFO[125]))
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


    def make_file_with_basic_info(self):
        '''
        creates file with basic informations about this specific supervisor object
        :return: nothing
        '''
        info_to_save = {
            'TLname'    : self.get_TLname(),
            'suitname'  : self.get_suitname(),
            'job_params': self.get_job_parameters()
        }
        with open(self.file_with_basic_info_path, 'wb') as file_with_basic_info:
            json.dump(info_to_save, file_with_basic_info)


    def delete_file_with_basic_info(self):
        if not os.path.exists(self.file_with_basic_info_path):
            pass
        else:
            for _ in range(10):
                try:
                    os.remove(self.file_with_basic_info_path)
                    break
                except:
                    time.sleep(0.1)


    def finish_with_failure(self):
        self.send_information_about_executed_job()
        self.delete_file_with_basic_info()
        logger.critical('{} : {}'.format(LOGGER_INFO[130], self.get_test_end_status()))
        sys.exit(1)


    def set_node_for_job(self):
        try:
            job_config_xml = ET.fromstring(self.get_job_handler().get_config())
            assignedNode_tag = job_config_xml.find('assignedNode')
            assignedNode_tag.text = str(self.get_TLname())
            self.get_job_handler().update_config(ET.tostring(job_config_xml))
            logger.debug("Updated TL name: {} in job {}".format(self.get_TLname(), self.get_jobname()))
        except:
            self.set_test_end_status("JenkinsError")
            logger.critical('{} : {}'.format(self.get_TLname(), LOGGER_INFO[104]))
            self.finish_with_failure()


    def set_job_status(self):
        try:
            self.__jenkins_info['job_status'] = self.get_job_handler().get_build(self.get_job_build_number()).get_status()
        except:
            self.__jenkins_info['job_status'] = "UNKNOWN"
            self.set_test_end_status("JenkinsError")
            logger.critical('{} : {}'.format(self.get_jobname(),LOGGER_INFO[105]))
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
            self.set_test_end_status("JenkinsError")
            logger.critical('{} : {}'.format(self.get_jobname(),LOGGER_INFO[124]))
            self.finish_with_failure()
        elif job_status == "SUCCESS":
            pass


    def is_queued_or_running(self, once=False):
        while True:
            if self.get_job_handler().is_queued():
                time.sleep(3)
            else:
                break
        try:
            self.set_job_build_number(self.get_job_handler().get_last_buildnumber())
        except:
            logger.critical(LOGGER_INFO[124])
            self.set_test_end_status("JenkinsError")
            self.finish_with_failure()
        if once:
            return self.get_job_handler().is_queued_or_running()
        try:
            while True:
                if self.get_job_handler().is_queued_or_running():
                    time.sleep(3)       #TODO LONGER SLEEP LATER
                else:
                    return False
        except:
            self.set_test_end_status("JenkinsError")
            logger.critical('{} : {}'.format(self.get_jobname(),LOGGER_INFO[124]))
            self.finish_with_failure()


    def build_job(self):
        try:
            super(SuperVisor, self).build_job(jobname=self.get_jobname(),
                                                      params=self.get_job_parameters())
            logger.info("Job {} was built".format(self.get_jobname()))
        except:
            self.set_test_end_status("JenkinsError")
            logger.critical('{}'.format(LOGGER_INFO[107]))
            self.finish_with_failure()


    def set_jenkins_console_output(self):
        try:
            self.set_job_output(self.get_job_handler().get_build(self.get_job_build_number()).get_console())
            logger.debug("Console output retrieved from {}".format(self.get_jobname()))
        except:
            self.set_test_end_status("JenkinsError")
            logger.error('{}'.format(LOGGER_INFO[108]))
            self.finish_with_failure()


    def check_job_output_for_filenames(self, match, regex):
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
        self.set_are_any_failed_tests(True)
        return matches


    def prepare_output_for_regex_matching(self, match):
        match = re.sub(" +", "_", match)  #changing " " to "_" - pybot thinks it's the same, i don't
        if match[-3:] == '...': match = match[:-3]  #cutting last "..."
        elif match[-1:] == '_': match = match[:-1]    #cutting last "_"
        return match


    def parse_output_and_set_job_failed_tests(self):
        job_filenames_failed_tests=[]
        try:
            matches = self.findall_test_failes()
            for match in matches:
                match = self.prepare_output_for_regex_matching(match)
                regexes = ['\w*\.Tests\.{}.*\.({}.*)'.format(self.get_suitname(), self.get_suitname()),
                         '\w*\.Tests\.({}.*)'.format(self.get_suitname()),
                         '\w*\.({}.*)'.format(self.get_suitname())]
                try:
                    job_filenames_failed_tests = [self.check_job_output_for_filenames(match, regex)
                                              for regex in regexes if self.check_job_output_for_filenames(match, regex)][0]
                    logger.info("Regex found fails in output of {}".format(self.get_jobname()))
                    self.set_test_end_status("GOT_FAILS")
                except:
                    pass
        except:
            logger.debug("Regex did not find fails in output of {}".format(self.get_jobname()))
        finally:
            self.set_filenames_of_failed_tests(job_filenames_failed_tests)
            self.check_output_for_other_fails_or_errors_and_set_test_end_status()


    def check_output_for_fails(self):
        output = self.get_job_output()
        if not output.find('| FAIL |') == -1:
            logger.debug("Found 'FAIL' in output of {}".format(self.get_jobname()))
            return True
        return False


    def check_output_for_errors(self):
        output = self.get_job_output().split('\n')
        for line in output:
            if re.findall('\[.ERROR.\].*no tests.*', line):
                self.write_suitename_to_testsWithoutTag_file_if_no_enable_tag_in_suite()
                logger.info('"{}" {}'.format(self.get_suitname(), LOGGER_INFO[131]))
                continue
            if not line.find('[ ERROR ]') == -1:
                logger.debug('{} "{}"'.format(LOGGER_INFO[132], self.get_jobname()))
                return True
        return False


    def check_output_for_other_fails_or_errors_and_set_test_end_status(self):
        if self.get_are_any_failed_tests() == False:
            if not self.check_output_for_fails() and not self.check_output_for_errors():
                self.set_test_end_status("SUCCESSFUL")
                # logger.debug('"{}" {}'.format(self.get_suitname(), LOGGER_INFO[133]))
            else:
                self.set_test_end_status("NOT_CAUGHT_ERROR/FAIL")
                self.set_are_any_failed_tests(True)
                logger.error('{}'.format(LOGGER_INFO[109]))
                self.finish_with_failure()

    def check_if_file_exists_and_create_if_not(self, path):
        if not os.path.exists(path):
            os.mknod(path)


    def clear_file(self, fd):
        fd.seek(0)
        fd.truncate()


    def remove_tag_from_testsWithoutTag_file_if_is_tag_in_suite(self):
        self.check_if_file_exists_and_create_if_not(self.testsWithoutTag_file_path)
        with open(self.testsWithoutTag_file_path, 'rb+') as testWithoutTag_file:
            lines_in_file = testWithoutTag_file.readlines()
            self.clear_file(testWithoutTag_file)
            [testWithoutTag_file.writelines('{}\n'.format(line_in_file))
             for line_in_file in lines_in_file if not json.loads(line_in_file) == self.get_suitname()]


    def write_suitename_to_testsWithoutTag_file_if_no_enable_tag_in_suite(self):
        self.check_if_file_exists_and_create_if_not(self.testsWithoutTag_file_path)
        with open(self.testsWithoutTag_file_path, 'rb+') as testsWithoutTag_file:
            lines_in_file = [json.loads(line) for line in testsWithoutTag_file.readlines()]
            try:
                suitename = [line for line in lines_in_file if line == self.get_suitname()][0]
                lines_in_file[lines_in_file.index(suitename)] += 1
                logger.info("'{}' {}".format(self.get_suitname(), LOGGER_INFO[130]))
            except:
                lines_in_file.append({self.get_suitname(): 1})
                logger.info("'{}' - {}".format(self.get_suitname(), LOGGER_INFO[131]))
            self.clear_file(testsWithoutTag_file)
            [testsWithoutTag_file.writelines('{}\n'.format(json.dumps(line))) for line in lines_in_file]
            # _found = False
            # to_write = []
            # for line in test_without_tag_file.readlines():
            #     line = json.loads(line.strip())
            #     if self.get_suitname() in line:
            #         _found = True
            #         line[self.get_suitname()] += 1
            #         if line[self.get_suitname()]%5 == 0:
            #             self.set_test_end_status("Tester slacking")
            #         to_write.append(line)
            #     else:
            #         to_write.append(line)
            # if not _found:
            #     to_write.append({self.get_suitname() : 1})
            # test_without_tag_file.seek(0)
            # test_without_tag_file.truncate(0)



    def __get_SSHClient_connection(self):
        try:
            SSHClient = paramiko.SSHClient()
            SSHClient.load_system_host_keys()
            SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            SSHClient.connect(self.get_TLaddress(), username='ute', password='ute')
            return SSHClient
        except:
            return None


    def __get_robot_filenames_and_paths(self):
        tmp_filenames_and_paths = []
        for root_path, directories, filenames in os.walk(self.suitename_folder_path):
            [tmp_filenames_and_paths.append({'path' : root_path, 'filename' : filename})
                                       for filename in filenames if filename.endswith('.robot') or filename.endswith('.txt')]
        return tmp_filenames_and_paths


    def __match_filenames_and_paths(self, tmp_filenames_and_paths):
        filenames_and_paths = []
        # filenames_and_paths_for_temporary_use = []
        for filename_from_output in self.get_filenames_of_failed_tests():
            matches = [(re.search('({}.*)'.format(filename_from_output), tmp_filename_and_path['filename']),
                        tmp_filename_and_path['path']) for tmp_filename_and_path in tmp_filenames_and_paths]
            [filenames_and_paths.append({'filename' : match[0].group(1), 'path' : match[1]}) for match in matches if match[0]]


            # _found = False
            # for tmp_filename_and_path in tmp_filenames_and_paths:
            #     try:
            #         re.search('({}.*)'.format(filename_from_output),tmp_filename_and_path['filename']).group(1)
            #         filenames_and_paths.append({'path' : tmp_filename_and_path['path'], 'filename' : tmp_filename_and_path['filename']})
            #         filenames_and_paths_for_temporary_use.append(tmp_filename_and_path['filename'])
            #         logger.debug("Found filename: {}".format(tmp_filename_and_path['filename']))
            #         _found = True
            #         break
            #     except:
            #         pass
            # if not _found:
            #     filenames_and_paths_for_temporary_use.append(filename_from_output)
            #     logger.warning('{} {}'.format(LOGGER_INFO[110],filename_from_output))
        self.set_filenames_of_failed_tests([tmp_filename_and_path['filename'] for tmp_filename_and_path in tmp_filenames_and_paths])
        return filenames_and_paths


    def remove_tag_from_robots_tests(self, old_tag = 'enable', new_tag = ''):
        tmp_filenames_and_paths = self.__get_robot_filenames_and_paths()
        filenames_and_paths = self.__match_filenames_and_paths(tmp_filenames_and_paths)
        SSHClient = self.__get_SSHClient_connection()
        if SSHClient == None:
            logger.warning('{}'.format(128))
            self.set_test_end_status("SSH_Connection_Failure")
            self.finish_with_failure()
        # __found = False
        print filenames_and_paths
        for filename_and_path in filenames_and_paths:
            try:
                SFTP = SSHClient.open_sftp()
                robot_file_path = os.path.join(filename_and_path['path'], filename_and_path['filename'])
                robot_file = SFTP.file(robot_file_path, 'r')
                print robot_file_path
                lines_in_robot_file = robot_file.readlines()
                matches = [re.search('(.*\[Tags].*)', line) for line in lines_in_robot_file]
                match = [match.group(1) for match in matches if match]
                print match[0]
                if match[0]:
                    lines_in_robot_file[lines_in_robot_file.index(match[0])] = re.sub(old_tag, new_tag, match[0])
                    logger.debug("{} '{}' : '{}' -> '{}'".format(LOGGER_INFO[132], robot_file_path, old_tag, new_tag))
                else:
                    logger.warning('"{}" {}'.format(old_tag, LOGGER_INFO[129]))
                # for line in lines_in_robot_file:
                #     try:
                #         re.search('.*\[Tags](.*)', line).group(1)
                #         try:
                #             lines_in_robot_file[lines_in_robot_file.index(line)] = re.sub(old_tag, new_tag, line)
                #             __found = True
                #             logger.debug("Changed tag in robot_file: {} from {} to {}".format(os.path.join(filename_and_path['path'], filename_and_path['filename']), old_tag, new_tag))
                #         except:
                #             logger.warning('"{}" {}'.format(old_tag, LOGGER_INFO[129]))
                #     except:
                #         pass
                robot_file.close()
                file2 = SFTP.file(os.path.join(filename_and_path['path'], filename_and_path['filename']), 'w')
                file2.writelines(lines_in_robot_file)
                file2.close()
                # SSHClient.close()

            #   git_result = self.git_launch(file_info=[path, file_name])
            #   if not git_result == True:
            #         self.failureStatus = 114
            #         logger.warning('{} : {}'.format(LOGGER_INFO[self.failureStatus], git_result))
            #   logger.info("Git push successful on {}".format(self.TLname))

            except:
                logger.warning('{}'.format(LOGGER_INFO[112]))
            finally:
                SSHClient.close()
        # if not __found:
        #     logger.warning('{} : {}'.format(LOGGER_INFO[111], old_tag))


    def get_logs_link(self):
        if self.get_job_status() == "SUCCESS":
            t = self.get_job_handler().get_last_build().get_timestamp()
            build_time = '{}-{:02g}-{:02g}_{:02g}-{:02g}-{:02g}'.format(t.year, t.month, t.day, (t.hour-(time.altzone/3600)), t.minute, t.second)
            logs_url_address = 'http://10.83.200.35/~ltebox/logs/{}_{}/log.html'.format(self.__TLname, build_time)
        else:
            logs_url_address = '{url}/job/{job_name}/{bn}/console'.format(url= 'http://plkraaa-jenkins.emea.nsn-net.net:8080',
                                                                  job_name=self.get_jobname(),
                                                                  bn=self.get_job_handler().get_last_buildnumber())
        return logs_url_address


    def choose_recipent_name(self):
        if self.get_user_info():
            recipent_name = "{} {}".format(self.get_user_info()['first_name'],
                                           self.get_user_info()['last_name'])
        else:
            if self.get_test_end_status() == "GOT_FAIL" or self.get_test_end_status() == "Tester slacking":
                recipent_name = "Tester"
            else:
                recipent_name = "Admin"
        return recipent_name


    def set_mail_message_and_subject(self):
        test_end_status = self.get_test_end_status()
        messages = []

        if test_end_status == "SUCCESSFUL":
            if self.get_user_info():
                _message = "Dear {}!\n\n" \
                           "Your test '{}' status is {}\n" \
                           "Logs are available at {}\n\n" \
                           "Have a nice day!".format(self.choose_recipent_name(),
                                                     self.get_suitname(),
                                                     self.get_job_status(),
                                                     self.get_logs_link())
                messages.append({'message' : _message})
                subject = "Test status update"
            else:
                return (0, 0)

        elif test_end_status == "GOT_FAILS":
            t = self.get_job_handler().get_last_build().get_timestamp()
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
                        "Logs are available at: {logs_link}\n\n" \
                        "Have a nice day!".format(self.choose_recipent_name(),
                                                  test_info=failed_tests_information,
                                                  logs_link=logs_url_address)
            messages.append({'message' : _message,
                            'feature' : self.get_suitname()})
            subject = "Tests status update - finished with fail"


        elif test_end_status == 'NOT_CAUGHT_ERROR/FAIL':
            logs_url_address = '{url}/job/{job_name}/{bn}/console'.format(url= 'http://plkraaa-jenkins.emea.nsn-net.net:8080',
                                                                  job_name=self.get_jobname(),
                                                                  bn=self.get_job_build_number())
            _message = "Dear {}! \n\n" \
                       "Tests on {tl_name} occured unknown fail.\n" \
                       "Please check logs available at: {logs_link} \n\n" \
                       "Have a nice day!".format(self.choose_recipent_name(),
                                                 tl_name=self.get_TLname(),
                                                 logs_link=logs_url_address)
            messages.append({'message' : _message})
            subject = "Tests status update - finished with unknown fail"


        elif test_end_status == 'JenkinsError':
            _message = "Dear {}! \n\n" \
                       "There is some problems with Jenkins. Please check it.\n\n" \
                       "Have a nice day!".format(self.choose_recipent_name())
            messages.append({'message' : _message})
            subject = "Tests status update - JenkinsError"


        elif test_end_status == 'SSH_Connection_Failure':
            _message = "Dear {}! \n\n" \
                       "There is some problems with SSH connection to Belvedere. Please check it.\n\n" \
                       "Have a nice day!".format(self.choose_recipent_name())
            messages.append({'message' : _message})
            subject = "Tests status update - SSHError"


        elif test_end_status == 'Tester slacking':
            _message = "Dear {}! \n\n" \
                       "You still didn't checked your test!\n" \
                       "Testsuite = '{}'. Please check it.\n\n" \
                       "Have a nice day!".format(self.choose_recipent_name(),
                                                 self.get_suitname())
            messages.append({'message' : _message,
                             'feature' : self.get_suitname()})
            subject = "Tests status update - You are slacking"
        return messages, subject

    def send_information_about_executed_job(self):
        (messages, subject) = self.set_mail_message_and_subject()
        if messages == 0 and subject == 0:
            return 0

        if self.get_user_info():
            recipents = self.get_user_info()['mail']
        else:
            if 'feature' in messages[0]:
                recipents = mail_dict[messages[0]['feature']]
            else:
                recipents = admin['mail']

        mail = ute_mail.mail.Mail(subject=subject,message=messages[0]['message'],
                                  recipients=recipents,
                                  name_from="Reservation Api")
        send = ute_mail.sender.SMTPMailSender(host = '10.150.129.55')
        send.connect()
        send.send(mail)
