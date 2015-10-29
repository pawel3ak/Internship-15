# -*- coding: utf-8 -*-
"""
:created on: '11/09/15'

:copyright: Nokia
:author: Paweł Nogieć
:contact: pawel.nogiec@nokia.com
"""

from ute_cloud_reservation_api.api import CloudReservationApi
import logging
from utilities.logger_messages import logging_messages
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
import copy
import ConfigParser
import threading


logger = logging.getLogger("server." + __name__)
logger_adapter = logging.LoggerAdapter(logger, {'custom_name': None})


class ReservationManager(CloudReservationApi):
    def __init__(self):
        self.config_file_path = os.path.join('.', 'server_config.cfg')
        self.config = ConfigParser.RawConfigParser()
        self.config.read(self.config_file_path)
        super(ReservationManager, self).__init__(
            api_token=self.config.get('ReservationManager', 'api_token'),
            api_address=self.config.get('ReservationManager', 'api_address'))
        self.__reservations_dictionary = {}
        self.backup_file_path = os.path.join('.', 'files', 'ReservationManager', 'backup.data')
        self.TL_map_file_path = os.path.join('.', 'utilities', 'TL_name_to_address_map.data')
        self.TL_blacklist_file_path = os.path.join('.', 'files', 'ReservationManager', 'blacklist.data')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.HOST = self.config.get('ReservationManager', 'host_ip')
        self.PORT = self.config.getint('ReservationManager', 'host_port')
        self.SMTP_SERVER_IP = self.config.get('ReservationManager', 'smtp_server_ip')
        self.socket.bind((self.HOST, self.PORT))
        self.socket.listen(5)
        self.outputs = []
        self.MAXTL = self.config.getint('ReservationManager', 'max_tl')
        self.FREETL = self.config.getint('ReservationManager', 'free_tl')
        self._release_flag = False
        self.eNB_Build = None

    def handle_client_request_and_response(self, client_socket):
        client_request = client_socket.recv(1024).strip()
        if re.search("request\/get_testline&cloud=(.*)", client_request):
            client_socket.send(self.request_get_testline(client_request))
        elif re.search("request\/status_of_=(.*)", client_request):
            client_socket.send(self.get_reserved_TL_status(client_request))
        elif re.search("request\/free_testline\=(.*)", client_request):
            client_socket.send(self.request_free_testline(client_request))
        elif client_request == "request/manager_status":
            client_socket.send(self.is_I_am_working())
        elif re.search("request\/get_end_date_of_=(.*)", client_request):
            client_socket.send(self.request_get_end_date(client_request))
        elif re.search("request\/blacklist_remove_TL=(.*)", client_request):
            client_socket.send(self.delete_TL_from_blacklist_file(client_request))
        elif re.search('eNB_Build=(.*)', client_request):
            client_socket.send(self.set_eNB_build(client_request))
        elif re.search('request/release_TL=(.*)', client_request):
            client_socket.send(self.request_release_reservation(client_request))
        else:
            client_socket.send("Unknown command")

    def request_release_reservation(self, client_request):
        TLname = re.search('request/release_TL=(.*)', client_request)
        if TLname in self.get_reservation_dictionary():
            self.release_reservation(TLname)
            return TLname
        else:
            return "Wrong TLname"

    def set_eNB_build(self, client_request):
        print client_request
        self.eNB_Build = re.search('eNB_Build=(.*)', client_request).group(1)
        return self.eNB_Build

    def request_get_end_date(self, client_request):
        TLname = re.search("request\/get_end_date_of_=(.*)", client_request).group(1)
        if not TLname in self.get_reservation_dictionary():
            return "Wrong TLname"
        if self.get_reservation_status(TLname) == 3:
            return self.get_end_date(TLname, convert_unicode_to_datetime=False)
        else:
            return "TL preparing"

    def get_reserved_TL_status(self, client_request):
        TLname = re.search("request\/status_of_\=(.*)", client_request).group(1)
        try:
            status = self.get_reservation_status(TLname)
            if status < 3:
                return "Preparing"
            elif status > 3:
                return "Finished"
            else:
                return "Active"
        except:
            return "Wrong TL name"

    def is_I_am_working(self):
        return "Y"

    def request_get_testline(self, client_request):
        cloud = re.search("request\/get_testline&cloud=(.*).*", client_request).group(1)
        TLname = self.find_first_free_TL(cloud)
        if not TLname == -1:
            self.set_jobname_for_TL_in_dictionary(TLname, jobname=True)
            self.make_backup_file()
            return TLname
        else:
            return "No available TL"

    def request_free_testline(self, client_request):
        TLname = re.search("request\/free_testline=(.*)", client_request).group(1)
        if not TLname in self.get_reservation_dictionary():
            return "Testline is not reserved"
        elif not self.get_reservation_dictionary()[TLname]['job']:
            return "Testline is already free"
        else:
            self.set_jobname_for_TL_in_dictionary(TLname)
            self.make_backup_file()
            return TLname

    def _create_reservation(self):
        try:
            # ID = (super(ReservationManager, self).create_reservation(testline_type = "CLOUD_F", enb_build=self.eNB_Build, duration = 480))
            # ID = (super(ReservationManager, self).create_reservation(enb_build="FL00_FSM3_9999_151014_025747", testline_type = "CLOUD_L", state="commissioned", duration = 480))
            ID = (
                super(ReservationManager, self).create_reservation(enb_build=self.eNB_Build, testline_type="CLOUD_L", state="commissioned", duration=480))
            return ID
        except:
            return -103  # User max reservation count exceeded

    def _set_TLinfo(self, ID):
        while True:
            TLinfo = self.get_reservation_details(ID)
            if not TLinfo['testline']['name']:
                time.sleep(5)
            else:
                TLname = TLinfo['testline']['name']
                break
        self.__reservations_dictionary[TLname] = {'id': ID,
                                                  'job': False,
                                                  'cloud': self.get_testline_type(ID)
        }
        self.write_TL_address_to_TL_map_file(TLname)

    def get_release_flag(self):
        return self._release_flag

    def set_release_flag(self, flag):
        self._release_flag = flag

    def get_testline_type(self, ID):
        return super(ReservationManager, self).get_reservation_details(ID)['testline_type']

    def set_reservations_dictionary(self, dictionary):
        self.__reservations_dictionary = copy.deepcopy(dictionary)

    def get_reservation_dictionary(self):
        return self.__reservations_dictionary

    def set_jobname_for_TL_in_dictionary(self, TLname, jobname=False):
        self.__reservations_dictionary[TLname]['job'] = jobname

    def create_reservation_and_set_TL_info(self):
        try:
            ID = self._create_reservation()
            logger_adapter.info('{}'.format(logging_messages(115, ID=ID)))
            self._set_TLinfo(ID)
        except:
            if ID == -102:
                logger_adapter.warning('{}'.format(logging_messages(1102)))
            elif ID == -103:
                logger_adapter.warning('{}'.format(logging_messages(1103)))

    def get_TL_address_from_ute_reservation_api(self, TLname):
        return super(ReservationManager, self).get_reservation_details(self.get_reservation_dictionary()[TLname]['id'])['testline']['address']

    def release_reservation(self, TLname):
        try:
            return super(ReservationManager, self).release_reservation(self.get_reservation_dictionary()[TLname]['id'])
        except:
            logger_adapter.error('{}'.format(logging_messages(1104)))

    def cancel_reservation(self, TLname):
        try:
            return super(ReservationManager, self).release_reservation(self.get_reservation_dictionary()[TLname]['id'])
        except:
            logger_adapter.error('{}'.format(logging_messages(1104)))

    def find_first_free_TL(self, cloud):
        if self._release_flag:
            return -1
        _TLname = None
        try:
            for TLname in self.get_reservation_dictionary():
                if not self.get_reservation_dictionary()[TLname]['job'] and \
                                self.get_reservation_dictionary()[TLname]['cloud'] == cloud and \
                        self.check_if_TL_not_in_blacklist_file(TLname):
                    status = self.get_reservation_status(TLname)
                    if not status == 3:
                        continue
                    else:
                        _TLname = TLname
        finally:
            if not _TLname:
                return -1
            else:
                return _TLname

    def get_reservation_status(self, TLname):
        return super(ReservationManager, self).get_reservation_details(self.get_reservation_dictionary()[TLname]['id'])['status']

    def extend_reservation(self, TLname, duration=40):
        return super(ReservationManager, self).extend_reservation(
            self.get_reservation_dictionary()[TLname]['id'],
            duration=duration)

    def add_to_blacklist(self, TLname):
        # since we can't actually block TL, we're extending reservation by max_time == 180min
        #sending e-mail to admin and adding_to_our_blacklist_file
        self.extend_reservation(TLname, 180)
        self.write_TLname_to_blacklist_file(TLname)
        try:
            message = "TL {} added to blacklist. Please check it".format(TLname)
            subject = "TL blacklisted"
            mail = ute_mail.mail.Mail(subject=subject, message=message,
                                      recipients=admin['mail'],
                                      name_from="ReservationManager_Api")
            send = ute_mail.sender.SMTPMailSender(host=self.SMTP_SERVER_IP)
            send.connect()
            send.send(mail)
        except:
            logger_adapter.error('{}'.format(logging_messages(1105)))

    def remove_TL_from_reservations_dictionary(self, TLname):
        self.__reservations_dictionary.pop(TLname)

    def check_if_TL_reservation_didnt_expire_during_breakdown(self):
        for TLname in self.get_reservation_dictionary().keys():
            status = self.get_reservation_status(TLname)
            if status > 3:
                self.release_reservation(TLname)
                self.remove_TL_from_reservations_dictionary(TLname)
                self.make_backup_file()

    @staticmethod
    def convert_unicode_to_datetime(unicode):
        date = datetime.datetime.strptime(unicode.split('.')[0], '%Y-%m-%d %H:%M:%S')
        return date

    @staticmethod
    def convert_datetime_to_unicode(date):
        unicode = u'{}'.format(date.strftime('%Y-%m-%d %H:%M:%S'))
        return unicode

    def get_add_date(self, TLname, convert_unicode_to_datetime=True):
        add_date = super(ReservationManager, self).get_reservation_details(self.get_reservation_dictionary()[TLname]['id'])['add_date']
        if convert_unicode_to_datetime:
            return self.convert_unicode_to_datetime(add_date)
        else:
            return add_date

    def get_end_date(self, TLname, convert_unicode_to_datetime=True):
        end_date = super(ReservationManager, self).get_reservation_details(self.get_reservation_dictionary()[TLname]['id'])['end_date']
        if convert_unicode_to_datetime:
            return self.convert_unicode_to_datetime(end_date)
        else:
            return end_date

    def get_start_date(self, TLname):
        start_date = super(ReservationManager, self).get_reservation_details(self.get_reservation_dictionary()[TLname]['id'])['start_date']
        return self.convert_unicode_to_datetime(start_date)

    def get_job_from_reservation_dictionary(self, TLname):
        return self.get_reservation_dictionary()[TLname]['job']

    def check_all_TL_for_extending_or_releasing(self):
        for TLname in self.get_reservation_dictionary().keys():
            if self.get_reservation_status(TLname) < 3:  # TL not yet prepared
                continue
            elif self.get_reservation_status(TLname) > 3:
                self.release_reservation(TLname)
                self.delete_TL_address_from_TL_map_file(TLname)
                self.remove_TL_from_reservations_dictionary(TLname)
                self.make_backup_file()
            else:
                if (self.get_end_date(TLname) -
                        datetime.datetime.utcnow()).total_seconds() < 60 * 30:
                    self.extend_reservation(TLname)

                elif not self.get_job_from_reservation_dictionary(TLname) and \
                                (datetime.datetime.utcnow() - self.get_add_date(TLname)).total_seconds() > 60 * 60 * 24:
                    self.release_reservation(TLname)
                    self.delete_TL_address_from_TL_map_file(TLname)
                    self.remove_TL_from_reservations_dictionary(TLname)
                    self.make_backup_file()

                if self.get_release_flag():
                    if not self.get_job_from_reservation_dictionary(TLname):
                        self.release_reservation(TLname)
                        self.delete_TL_address_from_TL_map_file(TLname)
                        self.remove_TL_from_reservations_dictionary(TLname)
                        self.make_backup_file()

    @staticmethod
    def check_if_file_exists_and_create_if_not(path):
        if not os.path.exists(path):
            os.mknod(path)

    def make_backup_file(self):
        self.check_if_file_exists_and_create_if_not(self.backup_file_path)
        with open(self.backup_file_path, 'wb') as backup_file:
            for TLname in self.get_reservation_dictionary():
                backup_file.writelines(json.dumps({TLname: self.get_reservation_dictionary()[TLname]}) + "\n")

    def read_backup_file(self):
        self.check_if_file_exists_and_create_if_not(self.backup_file_path)
        with open(self.backup_file_path, 'rb') as backup_file:
            tmp_dictionary = {}
            [tmp_dictionary.update(json.loads(line)) for line in backup_file.readlines() if not line == '']
            self.set_reservations_dictionary(tmp_dictionary)

    def create_TL_name_to_address_map_from_file_output(self, TL_map_file):
        TL_map = {}
        [TL_map.update(json.loads(line)) for line in TL_map_file.readlines() if not line == '']
        return TL_map

    def clear_file(self, fd):
        fd.seek(0)
        fd.truncate()

    def write_TL_address_to_TL_map_file(self, TLname):
        self.check_if_file_exists_and_create_if_not(self.TL_map_file_path)
        with open(self.TL_map_file_path, 'rb+') as TL_map_file:
            TL_map = self.create_TL_name_to_address_map_from_file_output(TL_map_file)
            if TLname not in TL_map:
                TL_map[TLname] = self.get_TL_address_from_ute_reservation_api(TLname)
            self.clear_file(fd=TL_map_file)
            [TL_map_file.writelines(json.dumps({TLname: TL_map[TLname]}) + "\n") for TLname in TL_map]

    def delete_TL_address_from_TL_map_file(self, TLname):
        self.check_if_file_exists_and_create_if_not(self.TL_map_file_path)
        with open(self.TL_map_file_path, 'rb+') as TL_map_file:
            TL_map = self.create_TL_name_to_address_map_from_file_output(TL_map_file)
            if TLname in TL_map:
                TL_map.pop(TLname)
            self.clear_file(fd=TL_map_file)
            [TL_map_file.writelines(json.dumps({TLname: TL_map[TLname]}) + "\n") for TLname in TL_map]

    def write_TLname_to_blacklist_file(self, TLname):
        with open(self.TL_blacklist_file_path, "ab") as TL_blacklist_file:
            TL_blacklist_file.write('{}\n'.format(TLname))

    def check_if_TL_not_in_blacklist_file(self, TLname):
        self.check_if_file_exists_and_create_if_not(self.TL_blacklist_file_path)
        with open(self.TL_blacklist_file_path, "rb") as TL_blacklist_file:
            if [line.strip for line in TL_blacklist_file.readlines() if line.strip() == TLname]:
                return False
            else:
                return True

    def delete_TL_from_blacklist_file(self, client_request):
        TLname = re.search("request\/blacklist_remove_TL=(.*)", client_request).group(1)
        self.check_if_file_exists_and_create_if_not(self.TL_blacklist_file_path)
        with open(self.TL_blacklist_file_path, "rb+") as TL_blacklist_file:
            blacklist = TL_blacklist_file.readlines()
            self.clear_file(TL_blacklist_file)
            [TL_blacklist_file.writelines(_TLname) for _TLname in blacklist if not _TLname == TLname]
        return TLname

    def check_if_TLaddresses_in_file(self):
        [self.write_TL_address_to_TL_map_file(TLname) for TLname in self.get_reservation_dictionary()]

    def serve(self):
        inputs = [self.socket, sys.stdin]
        while True:
            try:
                inputready, outputready, exceptready = select.select(inputs, [], [])
            except select.error:
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


def managing_reservations():
    try:
        ReservManager = ReservationManager()
    except socket.error, err:
        logger_adapter.warning("Error while starting RM process: {}".format(err))
        return None
    ReservManager.read_backup_file()
    ReservManager.check_if_TL_reservation_didnt_expire_during_breakdown()
    ReservManager.check_if_TLaddresses_in_file()
    t = threading.Thread(target=ReservManager.serve)
    t.setDaemon(True)
    t.start()
    while True:
        TIME = 60  # how long should I sleep if there is no available TL
        print "Available TL on Cloud L = {}".format(ReservManager.get_available_tl_count_group_by_type()['CLOUD_L'])
        print "FreeTL = {}".format(ReservManager.FREETL)
        print "Len of dict = {}".format(len(ReservManager.get_reservation_dictionary()))
        print "MAXTL = {}".format(ReservManager.MAXTL)
        if ReservManager.get_available_tl_count_group_by_type()['CLOUD_L'] > ReservManager.FREETL:
            ReservManager.set_release_flag(False)
            if len(ReservManager.get_reservation_dictionary()) < ReservManager.MAXTL:
                TIME = 0.01
                print "creating reservation..."
                ReservManager.create_reservation_and_set_TL_info()
                print ReservManager.get_reservation_dictionary()
                ReservManager.make_backup_file()
        elif ReservManager.get_available_tl_count_group_by_type()['CLOUD_L'] == ReservManager.FREETL:
            pass
        else:
            ReservManager.set_release_flag(True)
        ReservManager.check_all_TL_for_extending_or_releasing()
        time.sleep(TIME)


if __name__ == "__main__":
    managing_reservations()
