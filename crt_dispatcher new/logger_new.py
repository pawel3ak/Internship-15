"""
CRT Dispatcher website:
https://confluence.int.net.nokia.com/display/RUFF/CRT+Dispatcher
"""
import os
import sys
import logging
from crt_dispatcher import config

__author__ = 'Pawel Tarsa'
__copyright__ = 'Copyright 2015, Nokia'
__version__ = '2016-01-11'
__maintainer__ = 'Pawel Tarsa'
__email__ = 'pawel.tarsa@nokia.com'


class Logger(object):
    """
    Custom logging utilities for crt_dispatcher framework. It works both under windows family and linux OS.
    :param: owner - body of object where logger is using.
    e.g.
        class X():
            def __init__():
                self._logger = Logger(owner=self)
                self._logger.debug('First message.')
    """

    DEBUG_LOG_NAME = 'DEBUG_log.txt'
    INFO_LOG_NAME = 'INFO_log.txt'

    PRECISE_FORMAT = "%(asctime)s %(name)s %(threadName)s no.:%(thread)s %(levelname)-7s |%(message)s"
    SHORT_FORMAT = "%(asctime)s %(name)s %(levelname)-6s |%(message)s"

    def __init__(self, name='NoName', *args, **kwargs):
        self._stream_logging_level = logging.DEBUG  # config.Logger.get('stream_logging_level')
        self._file_logging_level = logging.DEBUG  # config.Logger.get('file_logging_level')
        self._output_dir = config.Logger.get('output_dir') #if sys.platform != 'win32' else "./"
        self._logger = logging.getLogger(name='crt_dispatcher.{}'.format(name[:25]))
        self._logger.setLevel(level=logging.DEBUG)
        self._configure_and_add_handlers()

    def header(self, msg, *args, **kwargs):
        self._logger.info(60 * "-")
        self._logger.info(" " + msg.upper(), *args, **kwargs)
        self._logger.info(60 * "-")

    def info(self, msg, *args, **kwargs):
        """Log 'msg % args' with severity 'INFO'."""
        self._logger.info(" " + msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """Log 'msg % args' with severity 'INFO'."""
        self._logger.debug(" " + msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Log 'msg % args' with severity 'WARNING'."""
        self._logger.warning(" " + msg.strip(), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Log 'msg % args' with severity 'WARNING'."""
        self._logger.error(" " + msg.strip(), *args, **kwargs)

    def _configure_and_add_handlers(self):
        if not self._logger.handlers:
            self._logger.addHandler(self._get_stream_handler(level=self._stream_logging_level,
                                                             formatter=ColoredFormatter()))
            self._logger.addHandler(self._get_file_handler(level=self._file_logging_level,
                                                           formatter=ColoredFormatter()))
            # self._logger.addHandler(self._get_file_handler(level=self._file_logging_level,
            #                                                file_path='INFO_log.txt',
            #                                                format=ColoredFormatter()))

    def _get_stream_handler(self, level, formatter=None):
        """Creates a stream (standard output to console) handler with given logging level"""
        _stream_handler = logging.StreamHandler()
        _stream_handler.setLevel(level)
        _stream_handler.setFormatter(fmt=formatter)
        return _stream_handler

    def _get_file_handler(self, level, formatter, file_path='DEBUG_log.txt'):
        if os.path.exists(self._output_dir + file_path):
            os.unlink(self._output_dir + file_path)  # it removes previous logger file. To discuss
        _file_handler = logging.FileHandler(file_path)
        _file_handler.setLevel(level)
        _file_handler.setFormatter(fmt=formatter)
        return _file_handler


class ColoredFormatter(logging.Formatter):

    PRECISE_FORMAT = "%(asctime)s %(name)-25s no.:%(thread)x %(levelname)-7s |%(message)s"

    def __init__(self):
        super(ColoredFormatter, self).__init__()
        self._fmt = "%(asctime)s %(name)-25s no.:%(thread)x %(levelname)-7s |%(message)s"

    def format(self, record):
        # if ishexrecord.thread = hex(record.thread)
        if r'.' in record.name:
            record.name = record.name.split(".")[1]
        if record.levelno == logging.DEBUG:
            record.msg = '\033[93m%s\033[0m' % record.msg
        elif record.levelno == logging.INFO:
            record.msg = '\033[91m%s\033[0m' % record.msg
        return logging.Formatter.format(self, record)
