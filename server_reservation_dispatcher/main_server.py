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


def main_server():
    server = MainServerApi(config_filename=CONFIG_FILE)
    server.get_data_from_config_file()
    server.create_server_dirs_if_not_exists()

    # start JobManager
    logger.info("Start new thread with checking loop")
    server.start_job_manager()

    server.set_up_server()
    logger.info("Start server loop - waiting for request")
    while True:
        [connection, data] = server.get_request_from_client()
        server.response_for_client_request(connection, data)
    server.stop_server()
    logger.info("Server stopped")


if __name__ == "__main__":
    main_server()
