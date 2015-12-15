"""
CRT Dispatcher website:
https://confluence.int.net.nokia.com/display/RUFF/CRT+Dispatcher
"""
from ute_cloud_common_api.exception import ApiParametersValidationFailException

from crt_dispatcher.messages.reservation import Reservation
from crt_dispatcher.messages.reservationready import ReservationReady
from crt_dispatcher.reservationnotifier import ReservationReadyNotifier
from concurrent.futures import ThreadPoolExecutor
from ute_cloud_reservation_api import api
from logger import Logger
from time import sleep
from Queue import PriorityQueue
import json
import config
import re

from tmp.udp_server import UDP_server

__author__ = 'Pawel Tarsa'
__copyright__ = 'Copyright 2015, Nokia'
__version__ = '2015-11-23'
__maintainer__ = 'Pawel Tarsa'
__email__ = 'pawel.tarsa@nokia.com'


class ReservationManager(object):

    @property
    def thread_pool_exec_description(self):
        return " (ThreadPoolExecutor) "

    @property
    def reservation_mgr_description(self):
        return " (ReservationManager) "

    def __init__(self):
        """
        Manage whole reservation process in CRT_dispatcher automation-tests framework.
        Used in:
            None, it is stand-alone part.

        :param:  None, all parameters are read from configuration file.
        :return: None
        """
        super(ReservationManager, self).__init__()
        configuration = config.ReservationManager
        self._server_handler = self._create_reservation_manager_handler()
        self._reservation_manager = api.CloudReservationApi(api_token=configuration['api_token'])
        self._server_udp = UDP_server(server_host=configuration['host_ip'],
                                      server_port=configuration['host_port'],
                                      handler=self._server_handler)
        self._messages_queue = PriorityQueue()
        self._max_number_of_tl_available_for_usage = configuration['max_tl']
        self._max_executor_workers = 10  # configuration['max_tl']
        self._reserved_testlines = []

    def run(self):
        """ Start all reservation manager actions.
            It makes in loop following actions:
                1. Checking if server got any messages
                    1.1
                        If yes, message is saving to _messages_queue (by nested handler)
                2. Starting appropriate action (create|release|extend reservation)
                    *** priority hierarchy: release priority && extend priority > create priority
                    2.1.
                        Creating action  --> starts threads which realizes run method from ReservationReadyNotifier,\
                                            saves booked reservation in memory and sends ReservationReady message to TestScheduler
                        Releasing action --> directly send request to cloud manager (using WRO api),\
                                            sends message to TestScheduler and removes concrete reservation from memory (_reserved_testlines)
                        Extending action --> directly send request to cloud manager (using WRO api)
        """
        with ThreadPoolExecutor(max_workers=self._max_number_of_tl_available_for_usage) as executor:
            while True:
                try:
                    self._server_udp.read()
                    sleep(0.1)
                    message_with_highest_priority = self._get_message_with_highest_priority()
                    self._start_adequate_action(executor=executor, message=message_with_highest_priority)
                except Exception as e:
                    raise   # to diagnose potential faults it raise exception

    def _get_message_with_highest_priority(self):
        if not self._messages_queue.empty():
            return self._messages_queue.get()

    def _start_adequate_action(self, executor, message):
        try:
            assert message is not None
        except:
            return
        msg_type = message['msg_type'].split('.')[0].encode('utf-8')
        reservation = Reservation(**message['reservation'])
        Logger.debug("Message with highest priority " + str(message))
        if msg_type == "createreservation":
            self._try_to_reserve_new_testline(executor=executor, reservation=reservation)
        if msg_type == "releasereservation":
            self._release_reservation(reservation=reservation)
        if msg_type == "extendreservation":
            self._extend_reservation(reservation)

    def _try_to_reserve_new_testline(self, executor, reservation):
        self.debug("Creating reservation...")
        notifier = ReservationReadyNotifier(Reservation(**reservation))
        executor.submit(notifier.run).add_done_callback(self._update_queues_and_send_confirmation_to_test_scheduler)
        self.debug("Reservation created.")

    def _release_reservation(self, reservation):
        self.debug("Releasing reservation...")
        try:
            id = self._reservation_manager.release_reservation(reservation_id=reservation.reservation_id)
            self.info(str(id))
            self._reserved_testlines.remove(reservation)
            self.debug("Reservation %d released." % id)
        except ApiParametersValidationFailException as e:
            self.error(str(e))
        except ValueError as ve:
            self.warn(str(ve))
        except Exception as e:
            self.error(str(e))


    def _extend_reservation(self, reservation):
        self.debug("Extending reservation...")
        try:
            id = self._reservation_manager.extend_reservation(reservation_id=reservation.reservation_id,
                                                              duration=reservation.extend_for)
            self.debug("Reservation %d extended." % id)
        except ApiParametersValidationFailException as e:
            self.error(str(e))
        except Exception as e:
            self.debug(e)

    def _update_queues_and_send_confirmation_to_test_scheduler(self, future):
        task_result = future._result
        if isinstance(task_result, ReservationReady):
            self._reserved_testlines.append(task_result['reservation'])
            self.debug("READY TL NOTIFICATIONS " + str(self._reserved_testlines))
            #TODO sending confirmation message to test scheduler.
            # self._server_udp.send(ReservationReady(Reservation(task_result['reservation'])))

    def _create_reservation_manager_handler(self):
        return ReservationManager.ReservationManagerHandler(self)

    def error(self, message, *args, **kwargs):
        """ Wrapper for common logger (to guarantee potential easy change common logger or add some additional options e.g. choose debug level) """
        Logger.error(message, *args, **kwargs)

    def warn(self, message, *args, **kwargs):
        """ Wrapper for common logger. Same as above """
        Logger.warn(self.reservation_mgr_description + message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        """ Wrapper for common logger. Same as above """
        Logger.debug(self.reservation_mgr_description + message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        """ Wrapper for common logger. Same as above """
        Logger.info(self.reservation_mgr_description + message, *args, **kwargs)

    class ReservationManagerHandler(object):
        """
            Custom Handler used only in ReservationManager.
        """
        @property
        def description(self):
            return " (ReservationManagerHandler) "

        def __init__(self, outer_instance):
            ''' It guard from situation in which nested class is created, but outer not. Factory-method used.
                Usage e.g.
                    * obj = OuterClass.InnerClass(self)
            '''
            self._outer_instance = outer_instance

        def _handle(self, message):
            try:
                message = json.loads(message)
                if re.match("create|release|extend", message['msg_type']):
                    self._outer_instance._messages_queue.put(message)
                else:
                    Logger.info("Messages does not transport information about class. It is only dict")
            except Exception as e:
                Logger.info(self.description + e.message)

if __name__ == '__main__':
    rm = ReservationManager()
    rm.run()

