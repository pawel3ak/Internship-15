"""
:created on: '04/09/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""
import json
import logging
from time import sleep
import ConfigParser
from job_manager_api import JobManagerApi

# create logger
logger = logging.getLogger("server." + __name__)
logger_adapter = logging.LoggerAdapter(logger, {'custom_name': None})


def start_suites_from_job_manager_dictionary(manager):
    manager.read_job_manager_dictionary_from_file()
    dictionary = manager.get_job_manager_dictionary()
    print dictionary
    for key in dictionary.keys():
        status = manager.get_tl_status_from_reservation_manager(key)
        if status == "Active":
            manager.start_new_supervisor(key, dictionary[key])
        elif not status:
            logger_adapter.debug("Connection error\\Wrong request")
        else:
            manager.remove_record_from_job_manager_dictionary(key)
    manager.write_job_manager_dictionary_to_file()


def fast_supervisors_start(manager):
    # TODO do it right and check or delete
    # not used
    queue_list = manager.read_all_records_from_queue()
    while True:
        tl_name = manager.get_tl_name_from_reservation_manager()
        if tl_name is None:
            break
        else:
            if len(queue_list) == 0:
                manager.write_queue_to_file(queue_list)
                manager.update_local_git_repository()
                manager.make_tests_queue_from_testsuites_dir()
                queue_list = manager.read_all_records_from_queue()
            next_suite = json.loads(queue_list.pop(0))
            manager.start_new_supervisor(tl_name, next_suite)


def managing_loop(manager, loop_interval):
    while True:
        logger_adapter.debug("Main JM loop")
        manager.delete_done_jobs_from_dictionaries()
        manager.write_job_manager_dictionary_to_file()
        while True:
            tl_name = manager.get_tl_name_from_reservation_manager()
            print tl_name
            if tl_name == "No available TL":
                logger_adapter.debug("No available TL")
                break
            elif tl_name == "Unknown command":
                logger_adapter.debug("Wrong request")
                break
            elif tl_name == "Connection error":
                logger_adapter.debug("Connection error")
                break
            else:
                if manager.get_queue_length() == 0:
                    manager.update_local_git_repository()
                    if not manager.make_tests_queue_from_testsuites_dir():
                        logger_adapter.debug("No suites to run - free TL in RM: {}".format(tl_name))
                        manager.free_testline_in_reservation_manager(tl_name)
                        break
                next_suite = manager.read_next_reservation_record_and_delete_from_queue()
                manager.start_new_supervisor(tl_name, next_suite)
        manager.write_job_manager_dictionary_to_file()
        sleep(loop_interval*60)


def job_manager(config_filename='server_config.cfg'):
    manager = JobManagerApi(config_filename)
    config = ConfigParser.RawConfigParser()
    config.read(config_filename)
    loop_interval = config.getfloat('JobManager', 'loop_interval')

    if not manager.start_reservation_manager():
        logger_adapter.critical("RM does not work")
        return None

    start_suites_from_job_manager_dictionary(manager)

    managing_loop(manager, loop_interval)


if __name__ == "__main__":
    pass
