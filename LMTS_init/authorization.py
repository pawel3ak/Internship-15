# -*- coding: utf-8 -*-
"""
:created on: '6/8/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nsn.com, pawel.nogiec@nokia.com
"""

import urllib2
import base64

def authorization(url, user = None, password = None): #TODO how user/pswd You've used?
    req = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (user, password)).replace('\n', '')
    req.add_header("Authorization", "Basic %s" % base64string)
    return req
