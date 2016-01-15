"""
CRT Dispatcher website:
https://confluence.int.net.nokia.com/display/RUFF/CRT+Dispatcher
"""
from datetime import datetime

import SocketServer
from ute_cloud_common_api.exception import ApiParametersValidationFailException
from crt_dispatcher.logger_new import Logger
from crt_dispatcher.messages.reservationready import ReservationReady
from time import sleep
from crt_dispatcher.tmp.decorators import suppress_insecure_platform_warnings
from messages.reservationcrashed import ReservationCrashed
from ute_cloud_proxy import UteCloudProxy

__author__ = 'Pawel Tarsa'
__copyright__ = 'Copyright 2015, Nokia'
__version__ = '2015-11-23'
__maintainer__ = 'Pawel Tarsa'
__email__ = 'pawel.tarsa@nokia.com'


class ReservationReadyNotifier(object):
    """
    Used in:
        Nowhere, it is stand-alone part.

    :param giveup_timeout: Number of minutes after which creating actions will be cancelled, and environment will be cleaned.
    :param reservation: Reservation object which contains all necessary information to make reservation
    :return:
        1. Positive case: Reservation object with filled items like: add_date, reservation_id etc.
        2. Negative case (e.g. Api exception) Reservation object with set on True item 'reservation_failed'
    """
    TESTLINE_STATUS_CHECKING_INTERVAL = 60

    def __init__(self, reservation, giveup_timeout=180):
        self._giveup_timeout = giveup_timeout
        self._start_time = None
        self._ute_cloud_proxy = UteCloudProxy()
        self._reservation = reservation
        self._logger = Logger(name="reservation_ready_notifier")

    @suppress_insecure_platform_warnings
    def run(self):
        self._logger.info("Run %s" % self._reservation)
        try:
            #return renewal reservation
            self._start_time = datetime.now()
            self._reservation = self._ute_cloud_proxy.create_reservation(reservation=self._reservation)
            if self._reservation.reservation_failed:
                self._logger.warning("Reservation failed. I know that here should be a reason and identifier but there isn't:\(")
                return ReservationCrashed(reservation=self._reservation)
            self._wait_until_testline_will_be_ready_to_use_or_time_goes_off()
            return ReservationReady(reservation=self._reservation)
        except ApiParametersValidationFailException as e:
            self._logger.info(e.type + e.message)
            return ReservationCrashed(reservation=self._reservation)  #TODO set reason why crashed
        except UnboundLocalError as e:
            self._logger.error(str(e))
            raise
        except Exception as e:
            self._logger.error(str(e))
            self._ute_cloud_proxy.cancel_reservation(reservation=self._reservation)

    def _wait_until_testline_will_be_ready_to_use_or_time_goes_off(self):
        while not (self._ute_cloud_proxy.is_reservation_canceled(self._reservation) or
                   self._ute_cloud_proxy.is_reservation_finished(self._reservation)):
            self._logger.info(self._ute_cloud_proxy.get_reservation_details(self._reservation))
            if self._ute_cloud_proxy.is_reservation_ready(self._reservation):
                break
            if self._is_giveup_timeout_reached():
                break
            sleep(ReservationReadyNotifier.TESTLINE_STATUS_CHECKING_INTERVAL)

    def _is_giveup_timeout_reached(self):
        time_delta = datetime.now() - self._start_time
        return True if time_delta.seconds > self._giveup_timeout*60 else False
