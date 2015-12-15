"""
CRT Dispatcher website:
https://confluence.int.net.nokia.com/display/RUFF/CRT+Dispatcher
"""
import os
import wrapt
import logging

__author__ = 'Tomasz Kolek'
__copyright__ = 'Copyright 2015, Nokia'
__version__ = '2015-11-24'
__maintainer__ = 'Pawel Tarsa'
__email__ = 'pawel.tarsa@nokia.com'


SHORT_FORMAT = '%(asctime)s %(levelname)-7s |%(message)s'
SHORT_FORMATTER = logging.Formatter(SHORT_FORMAT, datefmt='%I:%M:%S')
LONG_FORMAT = '%(asctime)s - %(levelname)-5s - %(message)s'
LONG_FORMATTER = logging.Formatter(LONG_FORMAT)
DEBUG_LOG_NAME = 'DEBUG_log.txt'
INFO_LOG_NAME = 'INFO_log.txt'


@wrapt.decorator
def translate_to_debug(wrapped, instance=None, args=(), kwargs={}):
    """
    Decorator to translate logs to debug level if logger is
    set to hide output messages e.g. in case of user input.
    """
    if Logger.hidden:
        Logger.debug(*args, **kwargs)
    else:
        return wrapped(*args, **kwargs)


class Logger(object):
    output_dir = "."
    real_logger = None
    hidden = False

    @staticmethod
    @translate_to_debug
    def header(msg, *args, **kwargs):
        """Log 'msg & arg' as header"""
        Logger._ensure_real_logger_created()
        Logger.real_logger.info(60 * "-")
        Logger.real_logger.info(" " + msg.upper(), *args, **kwargs)
        Logger.real_logger.info(60 * "-")

    @staticmethod
    @translate_to_debug
    def background(msg, *args, **kwargs):
        """Log 'msg & arg' as background"""
        Logger._ensure_real_logger_created()
        Logger.real_logger.info(" " * 4 + msg, *args, **kwargs)

    @staticmethod
    @translate_to_debug
    def info(msg, *args, **kwargs):
        """Log 'msg % args' with severity 'INFO'."""
        Logger._ensure_real_logger_created()
        Logger.real_logger.info(" " + msg, *args, **kwargs)

    @staticmethod
    def debug(msg, *args, **kwargs):
        """Log 'msg % args' with severity 'DEBUG'."""
        Logger._ensure_real_logger_created()
        Logger.real_logger.debug(msg, *args, **kwargs)

    @staticmethod
    @translate_to_debug
    def warning(msg, *args, **kwargs):
        """Log 'msg % args' with severity 'WARNING'."""
        Logger._ensure_real_logger_created()
        Logger.real_logger.warning(" " + msg.strip(), *args, **kwargs)

    @staticmethod
    @translate_to_debug
    def warn(msg, *args, **kwargs):
        """Log 'msg % args' with severity 'WARNING'."""
        Logger.warning(" " + msg.strip(), *args, **kwargs)

    @staticmethod
    @translate_to_debug
    def error(msg, *args, **kwargs):
        """Log 'msg % args' with severity 'ERROR'."""
        Logger._ensure_real_logger_created()
        Logger.real_logger.error(" " + msg.strip(), *args, **kwargs)

    @staticmethod
    def _ensure_real_logger_created():
        """Creates instance of real_logger if it does not exist"""
        if Logger.output_dir is None:
            raise LoggerNotInitialized("logger.output_dir needs to be set before first usage.")
        if Logger.real_logger is None:
            Logger.real_logger = Logger._create_real_logger()

    @staticmethod
    def _create_stream_handler(level):
        """Creates a stream (standard output to console) handler with given logging level"""
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(SHORT_FORMATTER)
        return stream_handler

    @staticmethod
    def _create_file_handler(file_path, level, formatter):
        """Creates a file handler with given path and logging level"""
        if os.path.exists(file_path):
            os.unlink(file_path)
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        return file_handler

    @staticmethod
    def _create_real_logger():
        """
        Creates a logger with one stream handler and
        two file handlers (one for INFO and one for DEBUG level)
        """
        logging.getLogger('paramiko.transport').addHandler(logging.NullHandler())
        real_logger = logging.getLogger('crt_dispatcher')
        real_logger.setLevel(logging.DEBUG)
        real_logger.addHandler(Logger._create_stream_handler(logging.DEBUG))
        # real_logger.addHandler(Logger._create_file_handler(os.path.join(Logger.output_dir, DEBUG_LOG_NAME),
        #                                                    logging.DEBUG, LONG_FORMATTER))
        # real_logger.addHandler(Logger._create_file_handler(os.path.join(Logger.output_dir, INFO_LOG_NAME),
        #                                                    logging.INFO, SHORT_FORMATTER))
        return real_logger


class LoggerNotInitialized(Exception):
    pass
