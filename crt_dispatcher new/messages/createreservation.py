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


class CreateReservation(InternalMessage):
    def __init__(self, reservation, *arg, **kwargs):
        """
        Send request for new testline reservation to ReservationReadyNotifier and
        order observation when testline will be ready to use.

        Direction:
        ReservationManager --> ReservationReadyNotifier

        :param reservation: Reservation object
        :param arg: Additional arguments
        :param kwargs: Additional arguments
        """
        super(CreateReservation, self).__init__(*arg, **kwargs)
        self['reservation'] = reservation
