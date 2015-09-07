"""
:created on: '17/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

import json
import logging
import os
import string

# create logger
logger = logging.getLogger("server." + __name__)


class ReservationQueue(object):
    def __init__(self, queue_file_path):
        self._queue_file_path = queue_file_path
        logger.debug("Create new queue object: {}".format(self._queue_file_path))
        if not os.path.exists(self._queue_file_path):
            os.mknod(self._queue_file_path)
        self._queue_length = self.__check_queue_length()

    def write_new_record_to_queue(self, record):
        with open(self._queue_file_path, "ab") as queue_file:
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

    def __check_queue_length(self):
        with open(self._queue_file_path, "rb") as queue_file:
            return len(queue_file.readlines())

    @staticmethod
    def __get_record_id_number():
        id_file = os.path.join("files", "temp_id")
        with open(id_file, "ab+") as opened_file:
            lines = opened_file.readlines()
            if len(lines) == 1:
                id_number = json.loads(lines[0]) + 1
            else:
                id_number = 1
            opened_file.seek(0)
            opened_file.truncate()
            json.dump(id_number, opened_file)
            return id_number

    @staticmethod
    def __generate_password(passw_length=4):
        import random
        alphabet = string.letters+string.digits
        ''.join(random.choice(alphabet) for _ in range(3))
        password = ""
        for i in range(passw_length):
            next_sign = random.randrange(len(alphabet))
            password += alphabet[next_sign]
        return password


if __name__ == "__main__":
    pass
