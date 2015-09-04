
"""
:created on: '13/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

from time import sleep
from threading import Thread
import os
import logging
import pexpect
import ConfigParser
from utilities.reservation_queue import ReservationQueue

# create logger
logger = logging.getLogger("server." + __name__)

# TODO - everything
class JobManagerApi(ReservationQueue):
    def __init__(self, config_filename = 'server_config.cfg'):
        self._config_filename = config_filename
        config = ConfigParser.RawConfigParser()
        config.read(config_filename)
        self._supervisors_handlers_dictionary = {}    # {reservation_ID: handler}
        self._job_manager_dictionary = {}      # {reservation_ID: suite_name}
        self._directory_with_tests = config.get('JobManager', 'directory_with_tests')
        ReservationQueue.__init__(os.path.join(config.get('JobManager', 'directory'),
                                               config.get('JobManager', 'queue_filename')))

    def __get_parameters_from_config_file(self, config_file_path):
        config = ConfigParser.RawConfigParser()
        config.read(config_file_path)

    def delete_done_jobs_from_dictionaries(self):
        for key in self._supervisors_handlers_dictionary.keys():
            if self._supervisors_handlers_dictionary[key].is_alive():    # check if job is finished
                # TODO - send info to ReservationMenager
                del self._supervisors_handlers_dictionary[key]
                del self._job_manager_dictionary[key]

    def start_new_job(self, reservation_id=None):
        if request is None:
            logger.debug("Get reservation from queue")
            request = queue.read_next_reservation_record_from_queue(queue_file)
            queue.delete_reservation_record_from_queue_file(queue_file, request["serverID"], request["password"])
        logger.info("Start new thread supervisor.main for serverID: {} reservationID: {}".format(request["serverID"], reservation_id))
        thread = Thread(target=supervisor.supervise, args=[request["serverID"],
                                                      request["reservation_data"],
                                                      server_dictionary,
                                                      request["jenkins_info"],
                                                      request["user_info"],
                                                      reservation_id])
        thread.daemon = True
        thread.start()
        logger.debug("Add thread to handle_dictionary")
        handle_dictionary[request["serverID"]] = thread


def get_list_of_folders_in_dir(directory):
    logger.debug("Get catalog list from directory: %s", directory)
    directory_list = []
    [directory_list.append(x) for x in os.listdir(directory) if os.path.isdir(os.path.join(directory, x))]
    return directory_list


def update_repository():
    logger.debug("Repository update")
    updating_bash = pexpect.spawn("/bin/bash")
    updating_bash.sendline("cd ~/auto/ruff_scripts")
    updating_bash.sendline("git pull")
    try:
        i = updating_bash.expect(["Already up-to-date", "remote"])
        if i == 1:
            updating_bash.expect("auto/ruff_scripts$", timeout=60)
    except pexpect.TIMEOUT:
        logger.error("Repository update - fail - timeout")


def make_tests_queue_from_dir(queue_file, directory, max_reservation_time):
    logger.debug("Make new queue")
    directory_list = get_list_of_folders_in_dir(directory)
    for dir in directory_list:
        request = {'reservation_data': {'testline_type': 'CLOUD_F',
                                        'duration': (60*max_reservation_time)},
                   'serverID': queue.get_server_id_number(),
                   'password': queue.generate_password(),
                   'user_info': None,
                   'jenkins_info': {'parameters': {'name': dir}}
                   }
        logger.debug("Write new queue to file: %s", queue_file)
        queue.write_to_queue_file(queue_file, request)





def checking_reservation_queue(queue_file_name, number_of_free_tl, max_tl_number, server_dictionary,
                               handle_dictionary, start_reservation_time, cloud_name='CLOUD_F', loop=True):
    test_reservation = TestLineReservation()
    while True:
        # temporary prints
        ##################################################################################################
        print "reservation loop"
        print "free tl on cloud_f = ", (test_reservation.get_available_tl_count_group_by_type())['CLOUD_F']
        print "free tl = ", number_of_free_tl
        print "ile lini w pliku = ", queue.check_queue_length(queue_file_name)
        print "max tl = ", max_tl_number
        print "dlugosc slownika = ", len(server_dictionary)
        ##################################################################################################
        logger.debug("Checking if we can reserve TL")
        if ((test_reservation.get_available_tl_count_group_by_type())[cloud_name] > number_of_free_tl) & \
                (len(server_dictionary) < max_tl_number):
            if queue.check_queue_length(queue_file_name) > 0:
                logger.debug("Start new job from queue")
                start_new_job(queue_file_name, server_dictionary, handle_dictionary)
            elif queue.check_queue_length(queue_file_name) == 0:
                logger.debug("Add tests to queue")
                update_repository()
                make_tests_queue_from_dir(queue_file_name, '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN', start_reservation_time)
                logger.debug("Start new job from queue")
                start_new_job(queue_file_name, server_dictionary, handle_dictionary)
            else:
                logger.warning("Some weird case ;/")
            sleep(3)
        else:
            break
        if not loop:
            break


def main_checking_loop(queue_file_name, server_dictionary_file_name,
                       number_of_free_tl, max_tl_number, server_dictionary, handle_dictionary,
                       min_time_to_end, start_reservation_time, max_reservation_time, extend_time):
    if len(server_dictionary) > 0:
        logger.info("Start processes for existing reservations")
        delete_done_reservation_from_dictionary(server_dictionary)
        for record in server_dictionary:
            start_new_job(queue_file_name, server_dictionary, handle_dictionary,
                          server_dictionary[record]["reservationID"],
                          dict(server_dictionary[record].items() + {"serverID": int(record)}.items()))
        logger.debug("Write server dictionary to file: %s", server_dictionary_file_name)
        serv_dictionary.write_dictionary_to_file(server_dictionary_file_name, server_dictionary)
    while True:
        logger.info("Main checking loop")
        logger.debug("Check TL busy")
        checking_tl_busy(server_dictionary, handle_dictionary, min_time_to_end, max_reservation_time, extend_time)
        logger.debug("Write server dictionary to file: %s", server_dictionary_file_name)
        serv_dictionary.write_dictionary_to_file(server_dictionary_file_name, server_dictionary)
        logger.debug("Check queue")
        checking_reservation_queue(queue_file_name, number_of_free_tl, max_tl_number,
                                   server_dictionary, handle_dictionary, start_reservation_time)
        logger.debug("Write server dictionary to file: %s", server_dictionary_file_name)
        serv_dictionary.write_dictionary_to_file(server_dictionary_file_name, server_dictionary)
        sleep(30)


if __name__ == "__main__":
    pass
