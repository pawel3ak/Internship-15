"""
:created on: '02/09/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""
import logging
import logging.handlers
import time
import os

LOG_DIRECTORY = "logs"


def add_handler(logger, formatter, logging_level= logging.INFO, filename_log= 'server.log'):
    file_handler = logging.handlers.TimedRotatingFileHandler(filename=os.path.join(LOG_DIRECTORY, filename_log),
                                                             when='midnight',
                                                             interval=1,
                                                             backupCount=30)
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def config_logger(logger):
    # create formatter
    formatter = logging.Formatter('%(asctime)s %(levelname)8s: %(name)30s - %(funcName)30s:     %(message)s',
                                  datefmt='%Y-%m-%d,%H:%M:%S')
    logging.Formatter.converter = time.gmtime

    # create catalog for logs if not exist
    if not os.path.isdir(LOG_DIRECTORY):
        os.makedirs(LOG_DIRECTORY)

    # handler for DEBUG lvl
    add_handler(logger, formatter, logging.DEBUG, 'server_debug.log')

    # handler for INFO lvl
    add_handler(logger, formatter, logging.INFO, 'server_info.log')

    # handler for WARNING, ERROR, CRITICAL lvl
    add_handler(logger, formatter, logging.WARNING, 'server_warn.log')
