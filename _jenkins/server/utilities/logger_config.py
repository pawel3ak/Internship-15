"""
:created on: '02/09/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""
import logging
import logging.handlers
import ConfigParser
import time
import os

LOG_DIRECTORY = "logs"


def config_logger(logger):
    # create formatter
    formatter = logging.Formatter('%(asctime)s %(levelname)8s: %(name)30s - %(funcName)30s:     %(message)s',
                                  datefmt='%Y-%m-%d,%H:%M:%S')
    logging.Formatter.converter = time.gmtime
    # create file handler to file with logs
    if not os.path.isdir(LOG_DIRECTORY):
        os.makedirs(LOG_DIRECTORY)

    # handler for DEBUG lvl
    file_handler = logging.handlers.TimedRotatingFileHandler(filename='logs/server.log',
                                                             when='midnight',
                                                             interval=1,
                                                             backupCount=30)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # handler for INFO lvl
    file_handler2 = logging.handlers.TimedRotatingFileHandler(filename='logs/server_info.log',
                                                              when='midnight',
                                                              interval=1,
                                                              backupCount=30)
    file_handler2.setLevel(logging.INFO)
    file_handler2.setFormatter(formatter)

    # handler for WARNING, ERROR, CRITICAL lvl
    file_handler3 = logging.handlers.TimedRotatingFileHandler(filename='logs/server_warn.log',
                                                              when='midnight',
                                                              interval=1,
                                                              backupCount=30)
    file_handler3.setLevel(logging.WARNING)
    file_handler3.setFormatter(formatter)

    # add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(file_handler2)
    logger.addHandler(file_handler3)
