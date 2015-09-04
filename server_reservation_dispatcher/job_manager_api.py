
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


class JobManager(object):
    def __init__(self):
        self._config = ConfigParser.RawConfigParser()
        self.__get_parameters_from_config_file('server_config.cfg')
        self._reservation_queue = ReservationQueue(os.path.join(self._config.get('JobManager', 'directory'),
                                                                self._config.get('JobManager', 'queue_filename')))
        self._handle_dictionary = {}
        self._

    def __get_parameters_from_config_file(self, config_file_path):
        self._config.read(config_file_path)



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


def start_new_job(queue_file, server_dictionary, handle_dictionary, reservation_id=None, request=None):
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


def finish_not_busy_reservation(server_id, server_dictionary, handle_dictionary, remove_tl_reservation=True):
    logger.debug("Get tl reservation ID")
    reservation_tl_id = server_dictionary[server_id]["reservationID"]
    logger.debug("Checking if thread is end for serverID: %d", server_id)
    handle_dictionary[server_id].join()
    if remove_tl_reservation & (reservation_tl_id is not None):
        logger.info("End reservation with ID: {}".format(reservation_tl_id))
        tl_reservation = TestLineReservation(reservation_tl_id)
        tl_reservation.release_reservation()
    logger.debug("Remove record from the dictionaries")
    del handle_dictionary[server_id]
    del server_dictionary[server_id]
    if not remove_tl_reservation:
        return reservation_tl_id
    return 0


def bind_new_job_to_tl(queue_file, server_id, server_dictionary, handle_dictionary):
    # check if job is finished, remove from dictionaries and get reservation ID number
    logger.debug("Get reservation ID and end finished job")
    reservation_id = finish_not_busy_reservation(server_id, server_dictionary, handle_dictionary, False)
    # add new job
    logger.debug("Start new job on existing reservation ID: %d", reservation_id)
    start_new_job(queue_file, server_dictionary, handle_dictionary, reservation_id)


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


def checking_tl_busy(server_dictionary, handle_dictionary, min_time_to_end, max_reservation_time, extend_time):
    logger.debug("Checking if same reservation are not busy")
    not_busy_record_list = serv_dictionary.get_not_busy_reservation_list(server_dictionary)
    for record in not_busy_record_list:
        finish_not_busy_reservation(record, server_dictionary, handle_dictionary)
        logger.debug("Finished job: %d", record)


def delete_done_reservation_from_dictionary(dictionary):
    temp = []
    for key in dictionary.keys():
        test_reservation = TestLineReservation(dictionary[key]["reservationID"])
        if test_reservation.get_reservation_details()["status"] > 3:    # reservation status is either canceled or finished
            del dictionary[key]


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
