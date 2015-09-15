"""
:created on: '17/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

import json
import logging
import os

# create logger
logger = logging.getLogger("server." + __name__)
logger_adapter = logging.LoggerAdapter(logger, {'custom_name': None})


class ReservationQueue(object):
    def __init__(self, queue_file_path):
        self._queue_file_path = queue_file_path
        logger_adapter.debug("Create new queue object: {}".format(self._queue_file_path))
        if not os.path.exists(self._queue_file_path):
            os.mknod(self._queue_file_path)
        self._queue_length = self.__check_queue_length()

    def get_queue_length(self):
        return self._queue_length

    def add_new_record_to_queue(self, record):
        with open(self._queue_file_path, "ab") as queue_file:
            json.dump(record, queue_file)
            queue_file.write("\n")
            self._queue_length += 1

    def write_new_record_list_to_queue(self, record_list):
        with open(self._queue_file_path, "wb") as queue_file:
            for record in record_list:
                json.dump(record, queue_file)
                queue_file.write("\n")
                self._queue_length += 1

    def read_next_reservation_record_and_delete_from_queue(self):
        with open(self._queue_file_path, "rb+") as queue_file:
            lines = queue_file.readlines()
            next_record = json.loads(lines.pop(0))
            queue_file.seek(0)
            queue_file.truncate()
            queue_file.writelines(lines)
            self._queue_length -= 1
        return next_record

    def read_all_records_from_queue(self):
        with open(self._queue_file_path, "rb") as queue_file:
            lines = queue_file.readlines()

    def write_queue_to_file(self, queue):
        with open(self._queue_file_path, "wb") as queue_file:
            queue_file.writelines(queue)
        self._queue_length = len(queue)

    def __check_queue_length(self):
        with open(self._queue_file_path, "rb") as queue_file:
            return len(queue_file.readlines())


if __name__ == "__main__":
    pass
