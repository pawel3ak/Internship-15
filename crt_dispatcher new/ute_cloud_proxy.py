"""
CRT Dispatcher website:
https://confluence.int.net.nokia.com/display/RUFF/CRT+Dispatcher
"""
import re

from ute_cloud_common_api.exception import ApiParametersValidationFailException, ApiActionNotPermittedException
from ute_cloud_reservation_api.api import CloudReservationApi
from ute_cloud_reservation_api.exception import ApiMaxReservationCountExceededException

from crt_dispatcher.config import ReservationManager as ReservationManagerConfig
from crt_dispatcher.logger_new import Logger

__author__ = 'Pawel Tarsa'
__copyright__ = 'Copyright 2015, Nokia'
__version__ = '2015-11-23'
__maintainer__ = 'Pawel Tarsa'
__email__ = 'pawel.tarsa@nokia.com'


class UteCloudProxy(CloudReservationApi):
    """
        Possible testlines status:
          - 'Pending for testline' (1)
          - 'Testline assigned'    (2)
          - 'Confirmed'            (3)
          - 'Finished'             (4)
          - 'Canceled'             (5)
    """

    def __init__(self):
        super(UteCloudProxy, self).__init__(api_token=ReservationManagerConfig['api_token'])
        self._logger = Logger(name="cloud_reservation_proxy")

    def create_reservation(self, reservation):
        #TODO change all item names in Reservation to avoid mis-match
        testline_type = reservation.tl_type
        enb_build = reservation.enb_build_name
        ute_build = None
        sysimage_build = None
        robotlte_revision = None
        state = None                           #TODO this should be added to reservation
        duration = reservation.duration
        try:
            reservation_id = super(UteCloudProxy, self).create_reservation(testline_type=testline_type,
                                                          enb_build=enb_build,
                                                          ute_build=ute_build,
                                                          sysimage_build=sysimage_build,
                                                          robotlte_revision=robotlte_revision,
                                                          state=state,
                                                          duration=duration)
            self._logger.info("Testline booked. Waiting for ready to use status...")
            reservation.reservation_id = reservation_id
            return reservation
        except ApiMaxReservationCountExceededException as e:
            """
                If this situation occurred, method returns None.
                Maybe there is better option.
            """
            self._logger.warning(e.message)
            reservation.reservation_failed = True
            return reservation  #TODO here different solution should be
        except Exception as e:
            self._logger.error(str(type(e)))
            raise

    def release_reservation_and_get_them(self, reservation):
        try:
#            super(UteCloudProxy, self).get_reservation_details(reservation.reservation_id)
            super(UteCloudProxy, self).release_reservation(reservation_id=reservation.reservation_id)
            self._logger.info("Testline released correctly.")
            return reservation
        except ApiParametersValidationFailException as e:
            self._logger.error(str(e))
            return reservation  #TODO it has to be changed!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        except ApiActionNotPermittedException as e:
            Logger.error("Releasing reservation not possible. " + str(e))

    def extend_reservation(self, reservation):
        try:
            super(UteCloudProxy, self).extend_reservation(reservation_id=reservation.reservation_id,
                                                          duration=reservation.duration)
            #TODO dates should be actualized
            return reservation
        except Exception:
            raise
        #TODO there should be handled this exception too.

    def cancel_reservation(self, reservation):
        """ You could cancel only existing reservation. Not finished and not already canceled. """
        if re.match(super(UteCloudProxy, self).get_reservation_status(reservation_id=reservation.reservation_id).encode('utf-8'), 'Confirmed|Pending for testline|Testline assigned'):
            super(UteCloudProxy, self).cancel_reservation(reservation_id=reservation.reservation_id)

    def is_reservation_ready(self, reservation):
        return True if super(UteCloudProxy, self).get_reservation_status(reservation_id=reservation.reservation_id).encode('utf-8') == 'Confirmed' else False

    def is_reservation_canceled(self, reservation):
        return True if super(UteCloudProxy, self).get_reservation_status(reservation_id=reservation.reservation_id).encode('utf-8') == 'Canceled' else False

    def is_reservation_finished(self, reservation):
        return True if super(UteCloudProxy, self).get_reservation_status(reservation_id=reservation.reservation_id).encode('utf-8') == 'Finished' else False

    def get_reservation_details(self, reservation):
        return str(super(UteCloudProxy, self).get_reservation_details(reservation_id=reservation.reservation_id))
