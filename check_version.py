# -*- coding: utf-8 -*-
"""
:created on: '6/8/15'

:copyright: NSN
:author: Pawel Nogiec
:contact: pawel.nogiec@nsn.com
"""

import urllib2
import re
from ssh_ import authorization

def check_ver_number():
    url = "http://infrastructure.emea.nsn-net.net/projects/btstools/lte_lmts/"
    site_data = str(urllib2.urlopen(url).read())

    site_data_matches = re.search('<a href="(.*)">R\d (LMTS latest build)<\/a>', site_data)
    url_latest_build = site_data_matches.groups()[0]

    site2_data = str(urllib2.urlopen(url_latest_build).read())
    site2_data_matches = re.search('artifacts are loc.*\s<.*="(.*)">', site2_data)
    url_from_site2_data = site2_data_matches.groups()[0]

    build_version = re.search('/R(\d{1,}.\d{1,})', url_from_site2_data)
    build_version = build_version.groups()[0]
    build_number = re.search('BLD-(.*)', url_from_site2_data)
    build_number = build_number.groups()[0]

    request = authorization(url_from_site2_data)
    lmts_versions_site_data = urllib2.urlopen(request)
    lmts_version_name = (re.search('<a href="(.*_amd64.deb)">', lmts_versions_site_data.read())).groups()[0]
    lmts_download_url = str(url_from_site2_data) + "/" + str(lmts_version_name)

    return build_version, build_number, lmts_download_url, lmts_version_name
