import json
import logging
from time import sleep
import ConfigParser
from job_manager_api import JobManagerApi

# create logger
logger = logging.getLogger("server." + __name__)


def start_suites_from_job_manager_dictionary(manager):
    manager.read_job_manager_dictionary_from_file()
    dictionary = manager.get_job_manager_dictionary()

    for key in dictionary.keys():
        # if reservation is still confirmed or less (<=3)
        if manager.get_tl_status_from_reservation_manager(key) < 4:
            manager.start_new_supervisor(key, dictionary[key])
        else:
            manager.remove_record_from_job_manager_dictionary(key)

    manager.write_job_manager_dictionary_to_file()


def fast_supervisors_start(manager):
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


def job_manager(config_filename='server_config.cfg'):
    manager = JobManagerApi(config_filename)
    config = ConfigParser.RawConfigParser()
    config.read(config_filename)
    loop_interval = config.getfloat('JobManager', 'loop_interval')

    manager.start_reservation_manager()

    # start_suites_from_job_manager_dictionary(manager)
    sleep(5)
    while True:
        print "1"
        manager.delete_done_jobs_from_dictionaries()
        manager.write_job_manager_dictionary_to_file()
        while True:
            print "loop"
            tl_name = manager.get_tl_name_from_reservation_manager()
            print tl_name
            if tl_name == "No available TL":
                break
            else:
                if manager.get_queue_length() == 0:
                    manager.update_local_git_repository()
                    manager.make_tests_queue_from_testsuites_dir()
                next_suite = manager.read_next_reservation_record_and_delete_from_queue()
                manager.start_new_supervisor(tl_name, next_suite)
        manager.write_job_manager_dictionary_to_file()
        sleep(loop_interval*60)
        print "3"
    print "end"


if __name__ == "__main__":
    pass
