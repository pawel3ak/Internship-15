"""
:created on: '02/09/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""
import ConfigParser
import logging
import logging.handlers
import time
import os


def add_handler(logger, formatter, logging_level=logging.INFO, log_file_path='server_log.log', when_backup='midnight',
                backup_interval=1, backup_count=30):
    file_handler = logging.handlers.TimedRotatingFileHandler(filename=log_file_path,
                                                             when=when_backup,
                                                             interval=backup_interval,
                                                             backupCount=backup_count)
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def config_logger(logger, config_filename):
    config = ConfigParser.RawConfigParser()
    config.read(config_filename)

    logger.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(config.get('Logger', 'formatter'),
                                  datefmt=config.get('Logger', 'date_fmt'))
    logging.Formatter.converter = time.gmtime

    # create catalog for logs if not exist
    if not os.path.isdir(config.get('Logger', 'directory')):
        os.makedirs(config.get('Logger', 'directory'))

    # handler for DEBUG lvl
    if config.getboolean('Logger', 'debug'):
        add_handler(logger, formatter, logging.DEBUG, os.path.join(config.get('Logger', 'directory'),config.get('Logger', 'debug_filename')),
                    config.get('Logger', 'when_backup'), config.getint('Logger', 'backup_interval'), config.getint('Logger', 'backup_count'))

    # handler for INFO lvl
    if config.getboolean('Logger', 'info'):
        add_handler(logger, formatter, logging.INFO, os.path.join(config.get('Logger', 'directory'),config.get('Logger', 'info_filename')),
                    config.get('Logger', 'when_backup'), config.getint('Logger', 'backup_interval'), config.getint('Logger', 'backup_count'))

    # handler for WARNING lvl
    if config.getboolean('Logger', 'warning'):
        add_handler(logger, formatter, logging.WARNING, os.path.join(config.get('Logger', 'directory'),config.get('Logger', 'warning_filename')),
                    config.get('Logger', 'when_backup'), config.getint('Logger', 'backup_interval'), config.getint('Logger', 'backup_count'))

    # handler for ERROR lvl
    if config.getboolean('Logger', 'error'):
        add_handler(logger, formatter, logging.ERROR, os.path.join(config.get('Logger', 'directory'),config.get('Logger', 'error_filename')),
                    config.get('Logger', 'when_backup'), config.getint('Logger', 'backup_interval'), config.getint('Logger', 'backup_count'))

    # handler for CRITICAL lvl
    if config.getboolean('Logger', 'critical'):
        add_handler(logger, formatter, logging.CRITICAL, os.path.join(config.get('Logger', 'directory'),config.get('Logger', 'criticalfilename')),
                    config.get('Logger', 'when_backup'), config.getint('Logger', 'backup_interval'), config.getint('Logger', 'backup_count'))

