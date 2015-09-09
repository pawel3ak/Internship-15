"""
:created on: '13/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""
import json

import os
import logging
import multiprocessing
import ConfigParser
import socket
from time import sleep
from utilities.reservation_queue import ReservationQueue
from superVisor import supervise
from server_git_api import git_launch
from reservation_manager_api import managing_reservations

# create logger
logger = logging.getLogger("server." + __name__)


class JobManagerApi(ReservationQueue):
    def __init__(self, config_filename='server_config.cfg'):
        self._config_filename = config_filename
        config = ConfigParser.RawConfigParser()
        config.read(config_filename)
        ReservationQueue.__init__(self, os.path.join(config.get('JobManager', 'directory'),
                                                     config.get('JobManager', 'queue_filename')))
        self._supervisors_handlers_dictionary = {}      # {reservation_ID: handler}
        self._job_manager_dictionary = {}               # {reservation_ID: suite_name}
        self._job_manager_dictionary_file_path = os.path.join(config.get('JobManager', 'directory'),
                                                              config.get('JobManager', 'JM_dictionary_filename'))
        if not os.path.exists(self._job_manager_dictionary_file_path):
            logger.debug("Make directory: {}".format(self._job_manager_dictionary_file_path))
            os.mknod(self._job_manager_dictionary_file_path)
        self._directory_with_testsuites = config.get('JobManager', 'directory_with_testsuites')
        self._reservation_manager_ip = config.get('ReservationManager', 'host_ip')
        self._reservation_manager_port = config.getint('ReservationManager', 'host_port')
        self._reservation_manager_handler = None

    def get_job_manager_dictionary(self):
        return self._job_manager_dictionary

    def remove_record_from_job_manager_dictionary(self, tl_name):
        del self._job_manager_dictionary[tl_name]

    def get_parameters_from_config_file(self):
        config = ConfigParser.RawConfigParser()
        config.read(self._config_filename)
        self._directory_with_testsuites = config.get('JobManager', 'directory_with_testsuites')

    def delete_done_jobs_from_dictionaries(self):
        for key in self._supervisors_handlers_dictionary.keys():
            # check if job is finished
            if not self._supervisors_handlers_dictionary[key].is_alive():
                logger.debug("Delete from dictionaries: {}".format(key))
                self.free_testline_in_reservation_manager(key)
                del self._supervisors_handlers_dictionary[key]
                del self._job_manager_dictionary[key]

    def make_tests_queue_from_testsuites_dir(self):
        logger.debug("Make new queue")
        directory_list = []
        [directory_list.append(x) for x in os.listdir(self._directory_with_testsuites)
            if os.path.isdir(os.path.join(self._directory_with_testsuites, x))]
        logger.debug("Write new queue to file")
        for directory in directory_list:
            jenkins_info = {'parameters': {'name': directory}}
            self.write_new_record_to_queue(jenkins_info)

    def start_new_supervisor(self, tl_name, jenkins_info, user_info=None):
        logger.info("Start new supervisor wit suite {} at TL name: {}".format(jenkins_info['parameters']['name'], tl_name))
        # TODO remove temp
        handle = multiprocessing.Process(target=supervise, args=('tl99_test', jenkins_info, user_info,))
        # handle = multiprocessing.Process(target=supervise, args=(tl_name, jenkins_info, user_info,))
        handle.start()
        print "start"
        logger.debug("Add process to dictionaries")
        self._supervisors_handlers_dictionary[tl_name] = handle
        self._job_manager_dictionary[tl_name] = jenkins_info

    def write_job_manager_dictionary_to_file(self):
        logger.debug("Write JM dictionary to file: {}".format(self._job_manager_dictionary_file_path))
        with open(self._job_manager_dictionary_file_path, "wb") as open_file:
            json.dump(self._job_manager_dictionary, open_file)

    def read_job_manager_dictionary_from_file(self):
        logger.debug("Read JM dictionary from file: {}".format(self._job_manager_dictionary_file_path))
        with open(self._job_manager_dictionary_file_path, "rb") as open_file:
            if len(open_file.readlines()) > 0:
                open_file.seek(0, 0)
                self._job_manager_dictionary = json.load(open_file)

    def start_reservation_manager(self):
        logger.info("Start new RM process")
        self._reservation_manager_handler = multiprocessing.Process(target=managing_reservations)
        self._reservation_manager_handler.start()
        while True:
            sleep(5)
            if self.check_reservation_manager_status():
                logger.info("Reservation Manager is working")
                break

    def stop_reservation_manager(self):
        self._reservation_manager_handler.join()

    def __send_request_to_rm_and_get_response(self, request):
        try:
            logger.debug("Connect to RM")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self._reservation_manager_ip, self._reservation_manager_port))
            logger.debug("Send request to RM: {}".format(request))
            sock.send(request)
            response = sock.recv(1024)
            logger.debug("Receive from RM: {}".format(response))
            sock.close()
            return response
        except socket.error, err:
            print err
            logger.error("Error in connection with RM: {}".format(err))
            return False

    def check_reservation_manager_status(self):
        return self.__send_request_to_rm_and_get_response("request/manager_status")

    def get_tl_name_from_reservation_manager(self):
        return self.__send_request_to_rm_and_get_response("request/get_testline")

    def get_tl_status_from_reservation_manager(self, tl_name):
        '''
        Get testline status as string.

        Status list:
            'Active'
            'Not active'
            'Wrong TL name'

        :param tl_name: string
        :return: string
        '''
        return self.__send_request_to_rm_and_get_response(("request/status_of_=" + tl_name))

    def free_testline_in_reservation_manager(self, tl_name):
        return self.__send_request_to_rm_and_get_response(("request/free_testline=" + tl_name))

    @staticmethod
    def update_local_git_repository():
        logger.debug("Update local git repository")
        git_launch('localhost', file_info=None, pull_only=True)


if __name__ == "__main__":
    job_manager = JobManagerApi()
    job_manager.start_reservation_manager()
    pass
