"""
:created on: '04/09/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""
import ConfigParser
import logging
import socket
import os
import multiprocessing
from job_manager import job_manager

logger = logging.getLogger("server" + __name__)


class MainServerApi(object):
    def __init__(self, host_ip=None, host_port=None, config_filename="server_config.cfg"):
        self._config_filename = config_filename
        self._host_ip = host_ip
        self._host_port = host_port
        self._server_socket = None
        self._job_manager_handler = None

    def set_config_filename(self, config_filename):
        self._config_filename = config_filename

    def get_config_filename(self):
        return self._config_filename

    def set_server_ip(self, host_ip):
        self._host_ip = host_ip

    def get_server_ip(self):
        return self._host_ip

    def set_server_port(self, host_port):
        self._host_port = host_port

    def get_server_port(self):
        return self._host_port

    def get_job_manager_handler(self):
        return self._job_manager_handler

    def get_data_from_config_file(self):
        config = ConfigParser.RawConfigParser()
        config.read(self._config_filename)
        self._host_ip = config.get('Server', 'host_ip')
        self._host_port = config.getint('Server', 'host_port')

    def set_up_server(self):
        logger.debug("Set up server config")
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self._host_ip, self._host_port))
        self._server_socket.listen(5)

    def get_request_from_client(self):
        client_connection, address = self._server_socket.accept()
        data = client_connection.recv(1024).strip()
        logger.debug("New request: {}".format(data))
        return [client_connection, data]

    def response_for_client_request(self, client_connection, data):
        if data == "test":
            client_connection.send("hello")
            logger.debug("Test command from client")
        else:
            logger.debug("Wrong command from client - send response and close client_connection")
            client_connection.send("Wrong command")
        client_connection.close()

    def create_server_dirs_if_not_exists(self):
        config = ConfigParser.RawConfigParser()
        config.read(self._config_filename)
        if not os.path.isdir(config.get('Server', 'directory')):
            os.makedirs(config.get('Server', 'directory'))
        if not os.path.isdir(config.get('ReservationManager', 'directory')):
            os.makedirs(config.get('ReservationManager', 'directory'))
        if not os.path.isdir(config.get('JobManager', 'directory')):
            os.makedirs(config.get('JobManager', 'directory'))
        if not os.path.isdir(config.get('SuperVisor', 'directory')):
            os.makedirs(config.get('SuperVisor', 'directory'))

    def start_job_manager(self):
        self._job_manager_handler = multiprocessing.Process(target=job_manager, args=(self._config_filename,))
        self._job_manager_handler.start()

    def stop_server(self):
        self._server_socket.close()
        self._job_manager_handler.join()
