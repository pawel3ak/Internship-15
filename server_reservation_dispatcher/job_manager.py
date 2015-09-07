from time import sleep
import ConfigParser
from job_manager_api import JobManagerApi

def job_manager(config_filename='server_config.cfg'):
    manager = JobManagerApi(config_filename)
    config = ConfigParser.RawConfigParser()
    config.read(config_filename)
    loop_interval = config.getfloat('JobManager', 'loop_interval')
    # TODO startup procedure
    '''
    start and wait for RM

    read job manager dictionary from file
    for key in job_man_dir.keys():
        check in RM if reservation is still confirmed or less (<=3)
        if yes
            start SV
        else
            del key


    '''

    while True:
        manager.delete_done_jobs_from_dictionaries()
        # TODO saving dictionary to file
        while True:
            # TODO get reservation from reservation manager
            '''
            get ID from RM
            if ID is not None:
                        get next from queue
                        start supervisor
            else
                        break
        save dictionary to file
        '''

        sleep(loop_interval*60)


if __name__ == "__main__":
    pass
