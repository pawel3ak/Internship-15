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


def job_manager(config_filename='server_config.cfg'):
    manager = JobManagerApi(config_filename)
    config = ConfigParser.RawConfigParser()
    config.read(config_filename)
    loop_interval = config.getfloat('JobManager', 'loop_interval')

    # TODO start and wait for RM

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
        while True:
            # TODO get reservation from reservation manager
            '''
            if ID is not None:
                        get next from queue(if len = 0 make queue)
                        start supervisor
            else
                        break
            save dictionary to file
            '''
            manager.write_job_manager_dictionary_to_file()
        sleep(loop_interval*60)


if __name__ == "__main__":
    pass
