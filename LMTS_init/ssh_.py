# -*- coding: utf-8 -*-
"""
:created on: '6/8/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nsn.com, pawel.nogiec@nokia.com
"""

import pexpect
import time
import re


import check_version
from lmts_downloader import download_given_SW_version

def _get_ssh_process(user, host):
    _ssh_command = "ssh {user}@{host}".format(user=user, host=host)
    _ssh_process = pexpect.spawn(_ssh_command)
    return _ssh_process

def _get_ssh_command_result(ssh_process):
    while True:
        match = ssh_process.expect(["password:", pexpect.EOF, pexpect.TIMEOUT])
        if match == 0:
            time.sleep(0.1)
            ssh_process.sendline('root')
            time.sleep(2)
            ssh_process.sendline('hversion')
            ssh_process.expect('Running Software Version: ')
            ssh_process.expect('\n')
            hversion_command_output = ssh_process.before
            return hversion_command_output

        elif match == 1:
            print "Connection error, child process has exited."
            raise
        elif match == 2:
            print "Connection timeout."
            raise #TODO maybe we should add some custom Exception(s)

def check_if_LMTS_SW_version_is_actual():
    _ssh_process = _get_ssh_process(user='root', host='10.60.0.11')
    _hversion_cmd_output = _get_ssh_command_result(ssh_process=_ssh_process)

    _current_LMTS_SW_version = re.search('R(\d{1,}.\d{1,}).*BLD-.*', _hversion_cmd_output).groups()[0]
    _LMTS_bld_number = (re.search('R\d{1,}.\d{1,}.*BLD-(.*)', _hversion_cmd_output).groups()[0])[:-1]
    print _hversion_cmd_output
    print _current_LMTS_SW_version, len(_current_LMTS_SW_version)
    print _LMTS_bld_number
    print len(_LMTS_bld_number)


    if _current_LMTS_SW_version == check_version.get_LMTS_bld_version() and _LMTS_bld_number == check_version.get_LMTS_bld_number():
        print "Latest version is already installed"
    else:
        download_given_SW_version(url = check_version.get_path_to_download_latest_LMTS_SW_version(),
                                                  lmts_version_name = check_version.get_LMTS_bld_name())


