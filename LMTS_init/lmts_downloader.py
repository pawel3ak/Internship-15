# -*- coding: utf-8 -*-
"""
:created on: '6/8/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nsn.com, pawel.nogiec@nokia.com
"""

import authorization
import urllib2

def download_given_SW_version(url, lmts_version_name):
    with open(lmts_version_name, "wb") as output:
        request = authorization(url)
        file_data = urllib2.urlopen(request)
        while True:
            chunk = file_data.read(1024*64)
            if not chunk: break
            output.write(chunk)
