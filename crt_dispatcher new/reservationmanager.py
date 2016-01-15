"""
CRT Dispatcher website:
https://confluence.int.net.nokia.com/display/RUFF/CRT+Dispatcher
"""
from ute_cloud_common_api.exception import ApiParametersValidationFailException

from crt_dispatcher.messages.reservation import Reservation
from crt_dispatcher.reservationnotifier import ReservationReadyNotifier
from concurrent.futures import ThreadPoolExecutor
from logger_new import Logger
from time import sleep
from Queue import PriorityQueue
import json
import config
import re

from tmp.udp_server import UDP_server
from crt_dispatcher.ute_cloud_proxy import UteCloudProxy

__author__ = 'Pawel Tarsa'
__copyright__ = 'Copyright 2015, Nokia'
__version__ = '2015-11-23'
__maintainer__ = 'Pawel Tarsa'
__email__ = 'pawel.tarsa@nokia.com'



class ReservationManager(object): #TODO actualization reserved_testlines

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
        self._ute_cloud_proxy = UteCloudProxy()
        self._server_udp = UDP_server(server_host=configuration['host_ip'],
                                      server_port=configuration['host_port'],
                                      handler=self._server_handler)
        self._messages_queue = PriorityQueue()
        self._max_number_of_tl_available_for_usage = configuration['max_tl']
        self._max_executor_workers = 10  # configuration['max_tl']
        self._reserved_testlines = []
        self._logger = Logger(name="reservation_manager")

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
        msg_type = self._get_message_type_from_message(message)
        reservation = self._get_reservation_from_message(message)
        self._logger.debug("Message with highest priority " + str(message))
        if msg_type == "createreservation":
            self._try_to_reserve_new_testline(executor=executor, reservation=reservation)
            return
        if msg_type == "extendreservation":
            self._extend_reservation(reservation)
            return
        if msg_type == "diagnosticreservation":
            self._logger.info("Diagnostic case. Only 4 tests.")
            return
        if msg_type == "releasereservation" and len(self._reserved_testlines) > 0:   #TODO it is under comment only becouse I want to clean environ
            self._release_reservation(reservation=reservation)
            return
        else: #TODO sth strange here? Why I've added this case?
            self._logger.warning("Releasing reservation failed. There are no reserved testlines."
                      " You should try cancel ongoing reservation")

    def _try_to_reserve_new_testline(self, executor, reservation):
        self._logger.debug("Creating reservation...")
        notifier = self._get_new_reservation_notifier(reservation=reservation)
        executor.submit(notifier.run).add_done_callback(self._update_queues_and_send_confirmation_to_test_scheduler)
        self._logger.debug("Reservation created.")

    def _get_message_type_from_message(self, message):
        return message['msg_type'].split('.')[0].encode('utf-8')

    def _get_reservation_from_message(self, message):
        return Reservation(**message['reservation'])

    def _get_new_reservation_notifier(self, reservation):
        return ReservationReadyNotifier(Reservation(**reservation))

    def _release_reservation(self, reservation):
        self._logger.debug("Releasing reservation...")
        try:
            released_reservation = self._ute_cloud_proxy.release_reservation_and_get_them(reservation=reservation)
            self._reserved_testlines.remove(released_reservation)
            self._logger.debug("Reservation %s released." % reservation)
        except ApiParametersValidationFailException as e:
            self._logger.error(str(e))
        except ValueError as ve:
            self._logger.ing(str(ve))
        except Exception as e:
            self._logger.error("Exception in _release_reservation method: " + str(e))

    def _extend_reservation(self, reservation):
        self._logger.debug("Extending reservation...")
        try:
            extended_reservation = self._ute_cloud_proxy.extend_reservation(reservation=reservation)
            self._update_reserved_testlines(updated_reservation=extended_reservation)
        except ApiParametersValidationFailException as e:
            self._logger.error(str(e))
        except Exception as e:
            self._logger.debug(e)

    def _update_queues_and_send_confirmation_to_test_scheduler(self, future):
        task_result = future._result
        if 'reservationready' in str(type(task_result)):   # sth wrong in this place
        # if isinstance(task_result, ReservationReady.__class__):
            self._reserved_testlines.append(task_result['reservation'])
            self._logger.debug("Reservation ready: " + str(self._reserved_testlines))
            #TODO sending confirmation message to test scheduler.
            # self._server_udp.send(ReservationReady(Reservation(task_result['reservation'])))
        if 'reservationcrashed' in str(type(task_result)):
            raise NotImplementedError

    def _send_confirmation_to_test_scheduler(self):
        raise NotImplementedError

    def _update_reserved_testlines(self, updated_reservation):
        self._reserved_testlines = [updated_reservation if updated_reservation.reservation_id == reservation.reservation_id else reservation for reservation in self._reserved_testlines]

    def _create_reservation_manager_handler(self):
        return ReservationManager._ReservationManagerHandler(self)


    class _ReservationManagerHandler(object):
        """
            Custom Handler used only in ReservationManager.
        """

        def __init__(self, outer_instance):
            ''' It guard from situation in which nested class is created, but outer not. Factory-method used.
                Usage e.g.
                    * obj = OuterClass.InnerClass(self)
            '''
            self._outer_instance = outer_instance

        def _handle(self, message):
            try:
                message = json.loads(message)
                if re.match("create|release|extend|diagnostic", message['msg_type']):
                    self._outer_instance._messages_queue.put(message)
                else:
                    self._outer_instance._logger.info("Messages does not transport information about class. It is only dict")
            except Exception as e:
                self._outer_instance._logger.info(self.description + e.message)
