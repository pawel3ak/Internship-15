# -*- coding: utf-8 -*-
"""
:created on: '11/08/15'

:copyright: Nokia
:author: Damian Papiez, Paweł Nogieć
:contact: damian.papiez@nokia.com, pawel.nogiec@nokia.com
"""

from ute_cloud_reservation_api.api import CloudReservationApi
from ute_cloud_reservation_api.exception import ApiMaxReservationCountExceededException
import logging
from utilities.logger_messages import LOGGER_INFO
from utilities.mailing_list import admin
import ute_mail.sender
import ute_mail.mail
import datetime
import os
import json
import socket
import time
import select
import re
import sys


logger = logging.getLogger("server" + __name__)

class ReservationManager(CloudReservationApi):
    def __init__(self):
        super(ReservationManager, self).__init__(api_token='99e66a269e648c9c1a3fb896bec34cd04f50a7d2', api_address='http://cloud.ute.inside.nsn.com')
        self.__reservations_dictionary = {}
        self.backup_file_path = os.path.join('.','files','ReservationManager','backup.data')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('127.0.0.1', 50010))
        self.socket.listen(5)
        self.outputs = []
        self.MAXTL = 2
        self.FREETL = 0


    def handle_client_request_and_response(self, client_socket):
        client_request = client_socket.recv(1024)
        if client_request == "request/get_testline":
            client_socket.send(self.request_get_testline())
        elif client_request == re.search("response\/tlname=(.*)\&jobname=(.*)", client_request):
            client_socket.send(self.response_jobname(client_request))
        elif client_request == re.search("request/free_testline=(.*)", client_request):
            client_socket.send()
        else:
            client_socket.send("Unknown command")


    def request_get_testline(self):
        TLname = self.find_first_free_TL()
        return TLname


    def response_jobname(self, client_request):
        match = re.search("response\/tlname=(.*)\&jobname=(.*)",client_request)
        TLname = match.group(1)
        jobname = match.group(2)
        self.set_jobname_for_TL_in_dictionary(TLname, jobname)
        return '{}&{}'.format(jobname, TLname)


    def request_free_testline(self, client_request):
        TLname = re.search("request/free_testline=(.*)", client_request).group(1)
        self.set_jobname_for_TL_in_dictionary(TLname)
        return TLname


    def __create_reservation(self):
        try:
            ID = (super(ReservationManager, self).create_reservation(testline_type = "CLOUD_F", duration = 480))
            if ID == 102:
                logger.warning('{}'.format(LOGGER_INFO[1102]))
                return 102
            elif ID == 103:
                logger.warning('{}'.format(LOGGER_INFO[1103]))
                return 103
            else:
                return ID
        except ApiMaxReservationCountExceededException:
            return -103  # User max reservation count exceeded


    def __set_TLinfo(self, ID):
        while True:
            TLinfo = self.get_reservation_details(ID)
            # print TLinfo
            if not TLinfo['testline']['name']:
                time.sleep(5)
            else:
                TLname = TLinfo['testline']['name']
                break
        TLadd_date = datetime.datetime.strptime(TLinfo['add_date'].split('.')[0],"%Y-%m-%d %H:%M:%S")
        #TLend_date = datetime.datetime.strptime(TLinfo['end_date'].split('.')[0],"%Y-%m-%d %H:%M:%S")
        print TLname
        TLend_date = TLadd_date.replace(hour=TLadd_date.hour + 8)
        self.__reservations_dictionary[TLname] = {'id' : ID,
                                                  'job' : None,
                                                  'add_date' : TLadd_date,
                                                  'end_date' : TLend_date,
                                                  'was_extended' : False
                                                  }


    def set_end_date(self, TLname):
        self.__reservations_dictionary[TLname]['end_date'] = \
            self.__reservations_dictionary[TLname]['end_date'].replace\
                (hour=self.__reservations_dictionary[TLname]['end_date'].hour + 2)


    def get_reservation_dictionary(self):
        return self.__reservations_dictionary


    def set_jobname_for_TL_in_dictionary(self,TLname, jobname=None):
        self.__reservations_dictionary[TLname]['job'] = jobname


    def create_reservation_and_set_TL_info(self):
        try:
            ID = self.__create_reservation()
            if ID ==102 or ID ==103:
                pass
            print ID
            self.__set_TLinfo(ID)
        except:
            logger.error('{}'.format(LOGGER_INFO[1104]))


    def release_reservation(self, TLname):
        try:
            return super(ReservationManager, self).release_reservation(self.get_reservation_dictionary()[TLname]['id'])
        except:
            logger.error('{}'.format(LOGGER_INFO[1104]))


    def cancel_reservation(self, TLname):
        try:
            return super(ReservationManager, self).release_reservation(self.get_reservation_dictionary()[TLname]['id'])
        except:
            logger.error('{}'.format(LOGGER_INFO[1104]))


    def find_first_free_TL(self):
        _TLname = None
        try:
            for TLname in self.get_reservation_dictionary():
                if not self.get_reservation_dictionary()[TLname]['job']:
                    status = self.get_reservation_status(TLname)
                    if status !=3:
                        continue
                    else:
                        _TLname = TLname

        except:
            pass
        finally:
            if not _TLname:
                return "No available TL"
            else:
                return _TLname


    def get_reservation_status(self, TLname):
        return super(ReservationManager, self).get_reservation_details(self.get_reservation_dictionary()[TLname]['id'])['status']


    def extend_reservation(self,TLname, duration = 30):
        ############### function not yet implemented by WRO
        return super(ReservationManager, self).extend_reservation(
            self.get_reservation_dictionary()[TLname]['id'],
            duration = duration)


    def add_to_blacklist(self, TLname):
        #since we can't actually block TL, we're extending reservation by one month (60min*24h*30days)
        #and sending e-mail to admin
        self.extend_reservation(TLname, (60*24*30))
        try:
            message = "TL {} added to blacklist. Please check it".format(TLname)
            subject = "TL blacklisted"
            mail = ute_mail.mail.Mail(subject=subject,message=message,
                                      recipients=admin['mail'],
                                      name_from="ReservationManager_Api")
            send = ute_mail.sender.SMTPMailSender(host = '10.150.129.55')
            send.connect()
            send.send(mail)
        except:
            logger.error('{}'.format(LOGGER_INFO[1105]))


    def periodically_check_all_TL_for_extending_or_releasing(self, no_free_TL):
        if True:
            for TLname in self.get_reservation_dictionary():
                TLinfo = self.get_reservation_dictionary()[TLname]
                if TLinfo['job']:
                            #and (TLinfo['end_date'] - datetime.datetime.utcnow()).total_seconds() < 60*30:
                    # self.extend_reservation(TLname,30)    #not yet
                    #self.set_end_date(TLname) #extend by 120min
                    pass
                elif (not TLinfo['job'] and no_free_TL == True) or \
                        (not TLinfo['job'] and
                                 (datetime.datetime.utcnow() -
                                      TLinfo['add_date']).total_seconds() > 60*60*24):
                    #no active job and less than <delta> available TL
                    #or
                    #no active job and reservation is longer than 24h (60s*60m*24h)
                    self.release_reservation(TLname)
                    self.set_jobname_for_TL_in_dictionary(TLname)   #actually we're deleting jobname
                elif (TLinfo['end_date'] - datetime.datetime.utcnow()).total_seconds() < 60*30:
                    # self.extend_reservation(TLname,120)    #not yet
                    #self.set_end_date(TLname) #extend by 120min
                    pass


    def make_backup_file(self):
        if not os.path.exists(self.backup_file_path):
            os.mknod(self.backup_file_path)
        with open(self.backup_file_path, 'rb+') as backup_file:
            data = backup_file.readlines()

            json.dump(self.get_reservation_dictionary(), backup_file)


    def read_backup_file(self):
        if not os.path.exists(self.backup_file_path):
            os.mknod(self.backup_file_path)
        else:
            with open(os.path.join('.','files','ReservationManager'), 'rb') as backup_file:
                backup_data = json.load(backup_file)
                print backup_data


    def serve(self):
        inputs = [self.socket, sys.stdin]
        while True:
            try:
                inputready, outputready, exceptready = select.select(inputs, [], [])
            except select.error, e:
                self.make_backup_file()
                break

            for s in inputready:

                if s == self.socket:
                    client_socket, address = self.socket.accept()
                    self.handle_client_request_and_response(client_socket)

                elif s == sys.stdin:
                    pass
                else:
                    pass





if __name__ == '__main__':
    import threading
#     MAX_TL = 3
#     free_TL = 1
    ReservManager = ReservationManager()
    t = threading.Thread(target=ReservManager.serve)
    t.setDaemon(True)
    t.start()
    while True:
        print "Available TL on Cloud F = {}".format(ReservManager.get_available_tl_count_group_by_type()['CLOUD_F'])
        print "FreeTL = {}".format(ReservManager.FREETL)
        print "Len of dict = {}".format(len(ReservManager.get_reservation_dictionary()))
        print "MAXTL = {}".format(ReservManager.MAXTL)
        if ReservManager.get_available_tl_count_group_by_type()['CLOUD_F'] > ReservManager.FREETL:
            if len(ReservManager.get_reservation_dictionary()) < ReservManager.MAXTL:
                print "no wzialbym cos..."
                ReservManager.create_reservation_and_set_TL_info()
                print "zarezerwowalem"
            else:
                pass
        ReservManager.periodically_check_all_TL_for_extending_or_releasing(no_free_TL=False)
        print ReservManager.get_reservation_dictionary()
        time.sleep(30)

#     # ReservManager.read_backup_file()
#     for availableTL in range(1,MAX_TL-free_TL):
#         ReservManager.create_reservation_and_set_TL_info()
#         time.sleep(1)
#         print ReservManager.get_reservation_dictionary()
#     # ReservManager.make_backup_file()
#     while True:
#         ReservManager.periodically_check_all_TL_for_extending_or_releasing(no_free_TL=False)
#         print ReservManager.get_reservation_dictionary()
#         time.sleep(30)
#
#
#
