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

logger = logging.getLogger("server" + __name__)

class ReservationManager(CloudReservationApi):
    def __init__(self, id=None):
        super(ReservationManager, self).__init__(api_token='99e66a269e648c9c1a3fb896bec34cd04f50a7d2', api_address='http://cloud.ute.inside.nsn.com')
        self.__reservations_dictionary = {}


    def create_and_bind_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.socket.bind

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
        TLinfo = self.get_reservation_details(ID)
        TLname = TLinfo['testline']['name']
        TLadd_date = datetime.datetime.strptime(TLinfo['add_date'].split('.')[0],"%Y-%m-%d %H:%M:%S")
        #TLend_date = datetime.datetime.strptime(TLinfo['end_date'].split('.')[0],"%Y-%m-%d %H:%M:%S")
        self.__reservations_dictionary[TLname] = {'ID' : ID,
                                                  'job' : None,
                                                  'add_date' : TLadd_date,
                                                  #'end_date' : TLend_date,
                                                  'was_extended' : False
                                                  }


    def get_reservation_dictionary(self):
        return self.__reservations_dictionary


    def set_jobname_for_TL_in_dictionary(self,TLname, jobname=None):
        self.__reservations_dictionary[TLname]['job'] = jobname


    def create_reservation_and_set_TL_info(self):
        try:
            ID = self.__create_reservation()
            if ID ==102 or ID ==103:
                pass
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
        for TLname in self.__reservations_dictionary:
            if not self.get_reservation_dictionary()[TLname]['job']:
                return TLname
            else:
                return 0


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
        while True:
            for TLname in self.get_reservation_dictionary():
                TLinfo = self.get_reservation_dictionary()[TLname]
                if TLinfo['job'] != None:
                            #and (TLinfo['end_date'] - TLinfo['add_date']).total_seconds() < 60*30:
                    # self.extend_reservation(TLname,30)    #not yet
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


    def make_backup_file(self):
        with open(os.path.join('.','files','ReservationManager'), 'wb') as backup_file:
            json.dump(self.get_reservation_dictionary(), backup_file)


    def read_backup_file(self):
        with open(os.path.join('.','files','ReservationManager'), 'wb') as backup_file:
            return json.load(backup_file)







    # def set_id(self, value):
    #     self.reservation_data['id'] = value
    #
    # def get_id(self):
    #     return self.reservation_data['id']

    # def set_address(self, value):
    #     self.reservation_data['address'] = value

    # def get_address(self):
    #     if self.reservation_data['id'] is None:
    #         print 'Reservation is not created'
    #         return -101
    #     if self.reservation_data['address'] is None:
    #         self.set_address(self.get_reservation_details()['testline']['address'])
    #     return self.reservation_data['address']


    #
    # def get_reservation_status(self):
    #     if self.reservation_data['id'] is None:
    #         print 'Reservation is not created'
    #         return -101
    #     return super(ReservationManager, self).get_reservation_status(self.reservation_data['id'])
    #
    # def get_reservation_details(self):
    #     if self.reservation_data['id'] is None:
    #         print 'Reservation is not created'
    #         return -101
    #     return super(ReservationManager, self).get_reservation_details(self.reservation_data['id'])
    #

    #

