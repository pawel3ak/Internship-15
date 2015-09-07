import json
from time import sleep
import ConfigParser
from job_manager_api import JobManagerApi


def start_suites_from_job_manager_dictionary(manager):
    manager.read_job_manager_dictionary_from_file()
    dictionary = manager.get_job_manager_dictionary()
    for key in dictionary.keys():
        # TODO check tl reservation in RM
        # if reservation is still confirmed or less (<=3)
        manager.start_new_supervisor(key, dictionary[key])

    '''
    else
        manager.remove_record_from_job_manager_dictionary(key)
    '''
    manager.write_job_manager_dictionary_to_file()


def start_jobs_as_much_as_possible(manager):
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

    start_suites_from_job_manager_dictionary(manager)

    '''
    TODO later
    start from queue to less files operation
    read all queue
    start all possible suites
    write to file
    '''

    while True:
        manager.delete_done_jobs_from_dictionaries()
        manager.write_job_manager_dictionary_to_file()
        while False:# True: TODO after do function in RM
            tl_name = manager.get_tl_name_from_reservation_manager()
            if tl_name is None:
                break
            else:
                if manager.get_queue_length() == 0:
                    manager.update_local_git_repository()
                    manager.make_tests_queue_from_testsuites_dir()
                next_suite = manager.read_next_reservation_record_and_delete_from_queue()
                manager.start_new_supervisor(tl_name, next_suite)
        manager.write_job_manager_dictionary_to_file()
        sleep(loop_interval*60)


if __name__ == "__main__":
    pass
