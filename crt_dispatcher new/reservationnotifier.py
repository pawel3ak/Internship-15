"""
CRT Dispatcher website:
https://confluence.int.net.nokia.com/display/RUFF/CRT+Dispatcher
"""
from ute_cloud_common_api.exception import ApiParametersValidationFailException
from ute_cloud_reservation_api import api
from crt_dispatcher.logger import Logger
from crt_dispatcher.messages.reservationready import ReservationReady
from crt_dispatcher.tmp.config import reservation_credentials
from time import sleep
import socket
from crt_dispatcher.tmp.decorators import suppress_warnings

__author__ = 'gtqk84 Michal Plichta'
__copyright__ = 'Copyright 2015, Nokia'
__version__ = '2015-11-17'
__maintainer__ = 'gtqk84 Michal Plichta'
__email__ = 'gtqk84@nokia.com'


class ReservationReadyNotifier(object):

    def __init__(self, reservation):
        self._cloud_reservation_manager = api.CloudReservationApi(api_token=reservation_credentials['token'])
        self._reservation = reservation
        self._log_prefix = " (ReservationReadyNotifier) "

    @suppress_warnings
    def run(self):
        print("RUN %s" % self._reservation)
        try:
            reservation_id = self._cloud_reservation_manager.create_reservation(testline_type=self._reservation.tl_type,
                                                                            enb_build=self._reservation.enb_build_name,
                                                                            ute_build=None,
                                                                            sysimage_build=None,
                                                                            robotlte_revision=None,
                                                                            state=None,
                                                                            duration=None)
            while self._cloud_reservation_manager.get_reservation_status(reservation_id).encode('utf-8') != ('Confirmed' and 'Canceled'):
                print self._cloud_reservation_manager.get_reservation_details(reservation_id)
                sleep(60)
                self._reservation['reservation_id'] = reservation_id
            #TODO if canceled then return none or sth like that
            print self._cloud_reservation_manager.get_reservation_details(reservation_id)
            self._reservation.reservation_id = reservation_id
        except ApiParametersValidationFailException as e:
            print "ApiParametersValidationFailException"
            print e
            raise
        except UnboundLocalError as e:
            print "UnboundLocalError"
            print e
            raise
        except Exception as e:
            print e
            self._cloud_reservation_manager.release_reservation(reservation_id=reservation_id)
        return ReservationReady(reservation=self._reservation)

    def _log(self, message, *args, **kwargs):
        Logger.debug(" [ReservationReadyNotifier] " + message, *args, **kwargs)

