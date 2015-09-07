# -*- coding: utf-8 -*-
"""
:created on: '11/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

from ute_cloud_reservation_api.api import CloudReservationApi
from ute_cloud_reservation_api.exception import ApiMaxReservationCountExceededException


class TestLineReservation(CloudReservationApi):
    def __init__(self, id=None, address=None, api_token='99e66a269e648c9c1a3fb896bec34cd04f50a7d2', api_address='http://cloud.ute.inside.nsn.com'):
        super(TestLineReservation, self).__init__(api_token, api_address)
        self.reservation_data = {'id': id, 'address': address}

    def __set_id(self, value):
        self.reservation_data['id'] = value

    def get_id(self):
        return self.reservation_data['id']

    def __set_address(self, value):
        self.reservation_data['address'] = value

    def get_address(self):
        if self.reservation_data['id'] is None:
            print 'Reservation is not created'
            return -101
        if self.reservation_data['address'] is None:
            self.__set_address(self.get_reservation_details()['testline']['address'])
        return self.reservation_data['address']

    def create_reservation(self, testline_type=None, enb_build=None, ute_build=None,
                           sysimage_build=None, robotlte_revision=None, state=None, duration=None):
        if self.reservation_data['id'] is not None:
            # print 'Reservation is already created'
            return -102
        try:
            self.__set_id(super(TestLineReservation, self).create_reservation(testline_type, enb_build, ute_build,
                                                                              sysimage_build, robotlte_revision, state, duration))
            return self.get_id()
        except ApiMaxReservationCountExceededException:
            # print 'User max reservation count exceeded'
            return -103  # User max reservation count exceeded

    def get_reservation_status(self):
        if self.reservation_data['id'] is None:
            print 'Reservation is not created'
            return -101
        return super(TestLineReservation, self).get_reservation_status(self.reservation_data['id'])

    def get_reservation_details(self):
        if self.reservation_data['id'] is None:
            print 'Reservation is not created'
            return -101
        return super(TestLineReservation, self).get_reservation_details(self.reservation_data['id'])

    def release_reservation(self):
        if self.reservation_data['id'] is None:
            print 'Reservation is not created'
            return -101
        return super(TestLineReservation, self).release_reservation(self.reservation_data['id'])

    def cancel_reservation(self):
        if self.reservation_data['id'] is None:
            print 'Reservation is not created'
            return -101
        return super(TestLineReservation, self).cancel_reservation(self.reservation_data['id'])


if __name__ == '__main__':
    print 'abc'
    #9:47 (11:47)
    # for i in range(68600,69200):
    reservation = TestLineReservation(70210)
    # print reservation.get_available_tl_count_group_by_type()
    # reservation = TestLineReservation(66567)
    # reservation = TestLineReservation(66626)
    # id = reservation.create_reservation(testline_type="CLOUD_F", duration=600)
    # if id == -103:
    #     print "max user"
    # if not isinstance(id, int):
    #     print "max user"
    #     if reservation.get_reservation_details()['user'] == 'app_lmts':
    # print reservation.get_address()
    print reservation.get_reservation_status()
    # print reservation.get_reservation_details()
    print reservation.release_reservation()
    # print reservation.get_address()
    print reservation.get_reservation_status()
    # print reservation.get_reservation_details()
