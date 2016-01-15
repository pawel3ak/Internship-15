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


class Reservation(InternalMessage):

    def __init__(self, enb_build_name=None, tl_type=None, priority=0, tl_name=None, reservation_id=None, tl_hostname=None, *arg, **kwargs):
        """
        Contains data regarding reservation test line in cloud and it use widly in crt dispatcher.

        Used in:
        TestScheduler, ReservationManager, ReservationReadyManager, UteCloudProxy, TestRunTracker

        :param enb_build_name: Name of eNB build i.e. FL00_FSM3_9999_151116_026483
        :param tl_type: Testline type i.e. CLOUD_L
        :param tl_name: Testline name i.e. IAV_KRA_CLOUD064
        :param reservation_id: Unique idetyfication of reservation
        :param tl_hostname: DNS name or IP address of VirtualMachine for testline
        :param arg: Additional arguments
        :param kwargs: Additional arguments

        HINT: If You want to use dict to creating Reservation (e.g. when You take a json message) then usage is as follow:
            r = Reservation(**message['reservation'])
        """
        super(Reservation, self).__init__(*arg, **kwargs)
        self['enb_build_name'] = enb_build_name
        self['tl_type'] = tl_type
        self['tl_name'] = tl_name
        self['reservation_id'] = reservation_id
        self['tl_hostname'] = tl_hostname
        self['priority'] = priority
        self['extend_for'] = 60
        self['password'] = None
        self['testline_address'] = None
        self['testline_name'] = None
        self['add_date'] = None
        self['start_date'] = None
        self['end_date'] = None
        self['reservation_failed'] = False
        if kwargs is not None:
            for key, val in kwargs.items():
                self[key] = val

    def __getattr__(self, item):
        if item in self.keys():
            return self[item]

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __cmp__(self, other):
        return cmp(other['priority'], self['priority'])

    def __eq__(self, other):
        return self['tl_type'] == other['tl_type'] and \
               self['tl_name'] == other['tl_name'] and \
               self['reservation_id'] == other['reservation_id'] and \
               self['enb_build_name'] == other['enb_build_name']

    def __str__(self):
        return 'Reservation' +\
               ' eNB build: ' + self['enb_build_name'] +\
               ' priority: ' + str(self['priority']) +\
               ' reservation_id: ' + (str(self['reservation_id']) if self['reservation_id'] else 'None')
