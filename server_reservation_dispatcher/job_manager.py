"""
:created on: '04/09/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""
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


def managing_loop(manager):
    logger_adapter.debug("Main JM loop")
    manager.update_build_name()
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


def job_manager(config_filename='server_config.cfg'):
    manager = JobManagerApi(config_filename)
    config = ConfigParser.RawConfigParser()
    config.read(config_filename)
    loop_interval = config.getfloat('JobManager', 'loop_interval')

    manager.start_reservation_manager()
    if not manager.is_reservation_manager_working():
        logger_adapter.critical("RM does not work")
        return None

    start_suites_from_job_manager_dictionary(manager)

    while True:
        managing_loop(manager)
        sleep(loop_interval*60)


if __name__ == "__main__":
    pass
