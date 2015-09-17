"""
:created on: '04/09/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

import logging
import logging.handlers
from utilities.logger_config import config_logger
from server_api import MainServerApi

CONFIG_FILE = 'server_config.cfg'


# create logger
logger = logging.getLogger("server")
config_logger(logger, CONFIG_FILE)
logger_adapter = logging.LoggerAdapter(logger, {'custom_name': None})


def main_server():
    server = MainServerApi(config_filename=CONFIG_FILE)
    server.get_data_from_config_file()
    server.create_server_dirs_if_not_exists()

    # start JobManager
    logger_adapter.info("Start new process with job manager")
    server.start_job_manager()

    server.set_up_server()
    logger_adapter.info("Start server loop - waiting for request")
    while True:
        [connection, data] = server.get_request_from_client()
        server.response_for_client_request(connection, data)
        if not server.is_job_manager_alive():
            logger_adapter.info("Job manager is not alive")
            break
    server.stop_server()
    logger_adapter.info("Server stopped")


if __name__ == "__main__":
    main_server()
