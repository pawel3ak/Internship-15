# -*- coding: utf-8 -*-
"""
:created on: '6/8/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nsn.com, pawel.nogiec@nokia.com
"""

import urllib2
import re
import authorization

LMTS_bld_info = {
                    'build_version'     : None,
                    'build_number'      : None,
                    'lmts_download_url' : None,
                    'lmts_version_name' : None,
}
URL = "http://infrastructure.emea.nsn-net.net/projects/btstools/lte_lmts/"

def _get_page_content(url):
    return str((urllib2.urlopen(url)).read())

def _get_intrested_part_of_page(site_data, regex_for_intrested_phrase):
    return re.search(regex_for_intrested_phrase, site_data).groups()[0]

def _find_and_save_all_neccessary_informations_in_given_page(url, **kwargs):
    pass

def save_LMTS_SW_info():
    LMTS_site_content = _get_page_content(URL)
    url_latest_bld = _get_intrested_part_of_page(site_data = LMTS_site_content,
                                                   regex_for_intrested_phrase='<a href="(.*)">R\d (LMTS latest build)<\/a>')

    site2_data = _get_page_content(url_latest_bld)
    url_from_site2_data = _get_intrested_part_of_page(site_data = site2_data,
                                                   regex_for_intrested_phrase='artifacts are loc.*\s<.*="(.*)">')

    build_version = _get_intrested_part_of_page(site_data=url_from_site2_data,
                                                regex_for_intrested_phrase='/R(\d{1,}.\d{1,})')

    build_number = _get_intrested_part_of_page(site_data=url_from_site2_data,
                                                regex_for_intrested_phrase='BLD-(.*)/')

    request = authorization(url_from_site2_data)    #TODO: add user/pswd like additional_params - raw_input to remove
    lmts_version_name = _get_intrested_part_of_page(site_data= _get_page_content(request),
                                                       regex_for_intrested_phrase= '<a href="(.*_amd64.deb)">')

    LMTS_bld_info["build_version"] = build_version
    LMTS_bld_info["build_number"] = build_number
    LMTS_bld_info["lmts_download_url"] = str(url_from_site2_data) + "/" + str(lmts_version_name)
    LMTS_bld_info["lmts_version_name"] = lmts_version_name

def get_LMTS_bld_version():
    return LMTS_bld_info["build_version"]

def get_LMTS_bld_number():
    return LMTS_bld_info["build_number"]

def get_LMTS_bld_name():
    return LMTS_bld_info["lmts_version_name"]

def get_path_to_download_latest_LMTS_SW_version():
    return LMTS_bld_info["lmts_download_url"]

"""
    save_LMTS_SW_info is main method of this script.
    This method should be run before usage of any method from this script (to fill in LMTS_bld_info dict)
"""
save_LMTS_SW_info()
