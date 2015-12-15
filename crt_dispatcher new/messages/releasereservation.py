"""
CRT Dispatcher website:
https://confluence.int.net.nokia.com/display/RUFF/CRT+Dispatcher
"""
from internalmessage import InternalMessage

__author__ = 'gtqk84 Michal Plichta'
__copyright__ = 'Copyright 2015, Nokia'
__version__ = '2015-11-24'
__maintainer__ = 'gtqk84 Michal Plichta'
__email__ = 'gtqk84@nokia.com'


class ReleaseReservation(InternalMessage):
    def __init__(self, reservation, *arg, **kwargs):
        """
        Send request for releasing testline reservation to ReservationManager.

        Direction:
        TestScheduler --> ReservationManager

        :param reservation: Reservation object
        :param arg: Additional arguments
        :param kwargs: Additional arguments
        """
        super(ReleaseReservation, self).__init__(*arg, **kwargs)
        self['reservation'] = reservation
