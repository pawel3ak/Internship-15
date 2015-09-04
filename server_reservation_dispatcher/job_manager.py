from time import sleep
from job_manager_api import JobManagerApi

def job_manager(config_filename):
    manager = JobManagerApi(config_filename)
    # TODO startup procedure

    while True:
        manager.delete_done_jobs_from_dictionaries()
        # TODO saving dictionary to file
        while True:
            # TODO get reservation from reservation manager
            '''
            if ID is not None:
                        get next from queue
                        start supervisor
            else
                        break
        save dictionary to file
        '''
