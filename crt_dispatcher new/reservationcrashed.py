"""
CRT Dispatcher website:
https://confluence.int.net.nokia.com/display/RUFF/CRT+Dispatcher
"""
from internalmessage import InternalMessage

__author__ = 'Pawel Tarsa'
__copyright__ = 'Copyright 2015, Nokia'
__version__ = '2015-11-23'
__maintainer__ = 'Pawel Tarsa'
__email__ = 'pawel.tarsa@nokia.com'


class ReservationCrashed(InternalMessage):
    def __init__(self, reservation, *arg, **kwargs):
        """
        Notify components that reservation cannot be realized.

        Direction:
        ReservationReadyNotifier --> ReservationManager

        :param reservation: Reservation object
        :param arg: Additional arguments
        :param kwargs: Additional arguments
        """
        super(ReservationCrashed, self).__init__(*arg, **kwargs)
        self['reservation'] = reservation
        self['fail_reason'] = None
