# -*- coding: utf-8 -*-
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
import sys
from mailing_list import mail_dict
import logging
from messages_logger import EXCEPTIONS_INFO
# create logger
logger = logging.getLogger("server." + __name__)


class Supervisor(object):
    def __init__(self, serverID, reservation_data, parent_dict, jenkins_info, user_info=None, TLreservationID=None):
        self.serverID = serverID
        if not 'duration' in reservation_data:
            self.failureStatus = 13
            logger.error('{}'.format(EXCEPTIONS_INFO[self.failureStatus]))
            self.finish_with_failure()
        self.reservation_data = reservation_data
        self.parent_dict = parent_dict
        self.jenkins_info = jenkins_info
        self.TLreservationID = TLreservationID
        self.user_info = user_info
        self.TLname = None
        self.TLaddress = None
        self.failureStatus = None
        self.has_got_fail = False
        self.test_end_status = None

    def get_serverID(self):
        return self.serverID

    def get_reservation_data(self):
        return self.reservation_data

    def get_parent_dict(self):
        return self.parent_dict

    def set_parent_dict(self, busy_status, job_tests_parsed_status=None):
        jenkins_info = self.jenkins_info.copy()
        if 'job_api' in jenkins_info:
            del jenkins_info['job_api']
        if 'console_output' in jenkins_info:
            del jenkins_info['console_output']
        self.parent_dict[self.serverID] = {
            'reservationID' : self.TLreservationID,
            'busy_status' : busy_status,
            'tl_name' : self.TLname,
            'duration' : self.reservation_data['duration'],
            'test_status' : job_tests_parsed_status,
            'jenkins_info': jenkins_info,
            'reservation_data' : self.reservation_data,
            'user_info' : self.user_info
        }
        logger.info("Saving parent dictionary")
        return self.parent_dict

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
        logger.info("Saving user informations : {} {}, email: {}".format(first_name,last_name,e_mail))
        return self.user_info

    def get_TLname(self):
        return self.TLname

    def get_TLname_from_ID(self):
        reservation = tlr.TestLineReservation(self.TLreservationID)
        return reservation.get_reservation_details()['testline']['name']

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
        self.parent_dict[self.serverID]['busy_status'] = False
        if test_status:
            self.test_end_status = test_status
        self.send_information(test_status=self.test_end_status)
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
            self.failureStatus = 1
            logger.warning('{}'.format(EXCEPTIONS_INFO[self.failureStatus]))
            self.finish_with_failure()
        elif self.TLreservationID == -102:
            self.failureStatus = 2
            logger.warning('{}'.format(EXCEPTIONS_INFO[self.failureStatus]))
            self.finish_with_failure()
        else:
            return self.TLreservationID

    def reservation_status(self):
        reservation = tlr.TestLineReservation(self.TLreservationID)
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
                self.failureStatus = 3      #reservation failure
                logger.warning('{} {}'.format(self.TLreservationID, EXCEPTIONS_INFO[self.failureStatus]))
                self.finish_with_failure()


    def update_TLname(self):
        try:
            job = self.jenkins_info['job_api'].get_job(self.jenkins_info['job_name'])
            job_config_xml = ET.fromstring(job.get_config())
            assignedNode_tag = job_config_xml.find('assignedNode')
            assignedNode_tag.text = str(self.TLname)
            job.update_config(ET.tostring(job_config_xml))
            return 0
        except:
            self.failureStatus = 4
            logger.warning('{} : {}'.format(self.TLname, EXCEPTIONS_INFO[self.failureStatus]))
            self.finish_with_failure()

    def get_job_status(self):
        job_status = None
        try:
            job = self.jenkins_info['job_api'].get_job(self.jenkins_info['job_name'])
            job_status = job.get_last_build().get_status()
        except:
            self.failureStatus = 5
            logger.error('{} : {}'.format(self.jenkins_info['job_name'],EXCEPTIONS_INFO[self.failureStatus]))
            self.finish_with_failure()
        finally:
            if job_status == "FAILURE":
                self.has_got_fail = False
                self.ending()
            else:
                return job.get_last_build().get_status()

    def get_is_queue_or_running(self):
        try:
            job = self.jenkins_info['job_api'].get_job(self.jenkins_info['job_name'])
            return job.is_queued_or_running()
        except:
            self.failureStatus = 5
            logger.error('{} : {}'.format(self.jenkins_info['job_name'],EXCEPTIONS_INFO[self.failureStatus]))
            self.finish_with_failure()

    def set_job_api(self):
        if not 'job_name' in self.jenkins_info:
            self.jenkins_info['job_name'] = 'test_on_{tl_name}'.format(tl_name=self.TLname)
        try:
            job_api = jenkinsapi.api.Jenkins('http://plkraaa-jenkins.emea.nsn-net.net:8080', username='nogiec', password='!salezjanierlz3!')
            self.jenkins_info['job_api'] = job_api
            return self.jenkins_info['job_api']
        except:
            self.failureStatus = 6
            logger.critical('{}'.format(EXCEPTIONS_INFO[self.failureStatus]))
            self.finish_with_failure()

    def create_and_build_job(self):
        try:
            self.update_TLname()
            self.jenkins_info['job_api'].build_job(jobname=self.jenkins_info['job_name'],
                                                   params=self.jenkins_info['parameters'])
            return 0
        except:
            self.failureStatus = 7
            logger.error('{}'.format(EXCEPTIONS_INFO[self.failureStatus]))
            self.finish_with_failure()

    def get_jenkins_console_output(self):
        try:
            job = self.jenkins_info['job_api'].get_job(self.jenkins_info['job_name'])
            while True:
                if not self.get_is_queue_or_running(): break
                else:
                    time.sleep(2)   ####TODO longer time on real tests
            self.jenkins_info['console_output'] = job.get_last_build().get_console()
            return self.jenkins_info['console_output']
        except:
            self.failureStatus = 8
            logger.error('{}'.format(EXCEPTIONS_INFO[self.failureStatus]))
            self.finish_with_failure()

    def get_job_tests_status(self):
        regex = r'\=\s(.*)\s\=\W*.*FAIL'
        tests_failed_list_with_dict=[]
        try:
            match = re.findall(regex,self.jenkins_info['console_output'])
            if len(match) != 0: self.has_got_fail = True
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
            # self.failureStatus = 9
            # logger.error('{}'.format(EXCEPTIONS_INFO[self.failureStatus]))
            # self.finish_with_failure(test_status="UNKNOWN_FAIL")
            pass
        finally:
            return tests_failed_list_with_dict

    def check_if_no_fails(self):
        output = ""
        try:
            output = self.jenkins_info['console_output']
        except:
            self.failureStatus = 8
            logger.error('{}'.format(EXCEPTIONS_INFO[self.failureStatus]))
            self.finish_with_failure(test_status="UNKNOWN_FAIL")

        if not output.find('| FAIL |') == -1:
            return False
        output = output.split('\n')
        for line in output:
            if re.findall('\[.ERROR.\].*no tests.*', line):
                ###mozna zapisac, ze tag ciagle nie zmieniony
                continue
            if not line.find('[ ERROR ]') == -1:
                return False
        return True

    def ending(self):
        if not self.has_got_fail:
            if self.check_if_no_fails() == True:
                self.test_end_status = "PASS"
            else:
                self.test_end_status = "UNKNOWN_FAIL"
                self.has_got_fail = True
                self.failureStatus = 9
                logger.error('{}'.format(EXCEPTIONS_INFO[self.failureStatus]))
                self.finish_with_failure(test_status=self.test_end_status)
        else:
            self.test_end_status = "Failed"
            self.has_got_fail = True
        return self.test_end_status

    def remove_tag_from_file(self, old_tag = 'enable', new_tag = ''):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.get_TLaddress(), username='ute', password='ute')
        sftp = client.open_sftp()
        additional_directory_list =[]
        files_names_list =[]
        path = None
        file_name = None
        for test in self.parent_dict[self.serverID]['test_status']:
            try:
                more_informations = re.search('({}.*)\.({}.*)'.format(test['test_name'],test['test_name']),
                                                test['file_name']).groups()
                additional_directory_list.append(more_informations[0])
                files_names_list.append(more_informations[1])
            except:
                files_names_list.append(test['file_name'])
                additional_directory_list.append('')

        for i in range(0,len(files_names_list)):
            if additional_directory_list[i] == '':
                path = '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/{}/tests/'.format(
                    self.parent_dict[self.serverID]['test_status'][i]['test_name'])

            else:
                path = '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/{}/tests/{}'.format(
                    self.parent_dict[self.serverID]['test_status'][i]['test_name'],
                    additional_directory_list[i])
            try:
                files = sftp.listdir(path=path)
                found = False
                for file in files:
                    try:
                        file_name = re.search('({name}.*)'.format(name=files_names_list[i]),file).groups()[0]
                        found = True
                        self.parent_dict[self.serverID]['test_status'][i]['file_name'] = file_name
                        break
                    except:
                        pass
                if not found:
                    self.failureStatus = 10
                    logger.warning('{}'.format(EXCEPTIONS_INFO[self.failureStatus]))
            except:
                pass
        try:
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
            if not found:
                self.failureStatus = 11
                logger.warning('{} : {}'.format(EXCEPTIONS_INFO[self.failureStatus], old_tag))
            file.close()
            file = sftp.open(os.path.join(path,file_name), 'w')
            file.writelines(lines_in_file)
            file.close()
        except:
            self.failureStatus = 12
            logger.warning('{}'.format(EXCEPTIONS_INFO[self.failureStatus]))
        finally:
            self.test_end_status = "Failed"
            client.close()

    def send_information(self, test_status=None):
        if test_status:
            self.test_end_status = test_status
        if self.test_end_status == "PASS":
            return 0
        elif self.test_end_status == None:
            self.test_end_status = 'UNKNOWN_FAIL'

        message = []
        subject = ""
        if self.test_end_status == "reserv_pending":
            _message = "Dear {f_name} {l_name}! \n\n" \
                       "Your reservation is pending.\n" \
                       "Reservation ID = {rID}\n" \
                       "Testline name = {tl_name}\n\n" \
                       "Have a nice day!".format(f_name=self.user_info['first_name'],
                                                 l_name=self.user_info['last_name'],
                                                 rID=self.TLreservationID, tl_name=self.TLname)
            message.append({'message' : _message})
            subject = "Reservation status update"


        elif self.test_end_status == "Failed":
            job = self.jenkins_info['job_api'].get_job(self.jenkins_info['job_name'])
            t = job.get_last_build().get_timestamp()
            build_time = '{}-{:02g}-{:02g}_{:02g}-{:02g}-{:02g}'.format(t.year, t.month, t.day, (t.hour-(time.altzone/3600)), t.minute, t.second)
            logs_link = 'http://10.83.200.35/~ltebox/logs/{}_{}/log.html'.format(self.TLname, build_time)
            test_info = ''
            print "test_status = ", self.parent_dict[self.serverID]['test_status']

            for test in self.parent_dict[self.serverID]['test_status']:
                test_info += "Test = {test_name}.{file_name}\n".format(
                    test_name=test['test_name'],
                    file_name=test['file_name'])
            _message = "Dear tester! \n\n" \
                        "Your test have failed: \n\n" \
                        "{test_info}\n\n" \
                        "Logs are available at: {logs_link}\n\n" \
                        "Have a nice day!".format(test_info=test_info,
                                                  logs_link=logs_link)
            message.append({'message' : _message,
                            'feature' : self.parent_dict[self.serverID]['test_status'][0]['test_name']})
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
            message.append({'message' : _message})
            subject = "Tests status update - finished with unknown fail"




        if 'feature' in message[0]:
            for message_number in range(0, len(message)):
                mail = ute_mail.mail.Mail(subject=subject,message=message[message_number]['message'],
                                          recipients=mail_dict[message[message_number]['feature']],
                                          name_from="Reservation Api")
                print mail_dict[message[message_number]['feature']]
                send = ute_mail.sender.SMTPMailSender(host = '10.150.129.55')
                send.connect()
                send.send(mail)
        else:
            mail = ute_mail.mail.Mail(subject=subject,message=message[0]['message'],
                                          recipients='pawel.nogiec@nokia.com',
                                          name_from="Reservation Api")
            send = ute_mail.sender.SMTPMailSender(host = '10.150.129.55')
            send.connect()
            send.send(mail)

