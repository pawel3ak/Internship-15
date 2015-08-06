# -*- coding: utf-8 -*-
"""
:created on: '6/8/15'

:copyright: NSN
:author: Pawel Nogiec
:contact: pawel.nogiec@nsn.com
"""

import pexpect
import time
import re
import urllib2
import base64

def authorization(url):
    u = raw_input("user: ")
    pw = raw_input("passwd: ")
    req = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (u, pw)).replace('\n', '')
    req.add_header("Authorization", "Basic %s" % base64string)
    return req

def main():
    LMTS_version = ""

    ssh_command = 'ssh root@10.60.0.11'
    ssh_process = pexpect.spawn(ssh_command)
    i = ssh_process.expect(["password:", pexpect.EOF, pexpect.TIMEOUT])
    if i == 0:
        time.sleep(0.1)
        ssh_process.sendline('root')
        time.sleep(2)
        ssh_process.sendline('hversion')
        ssh_process.expect('Running Software Version: ')
        ssh_process.expect('\n')
        LMTS_version = ssh_process.before
    elif i == 1:
        print "Connection error, child process has exited."
    elif i == 2:
        print "Connection timeout."


    LMTS_version = re.search('R(\d{1,}.\d{1,}).*BLD-(.*)',LMTS_version)
    build_version = LMTS_version.groups()[0]
    build_number = LMTS_version.groups()[1]
    from check_version import check_ver_number
    latest_build_version, latest_build_number, lmts_file_url, f_name = check_ver_number()

    if latest_build_version == build_version and latest_build_number == build_number:
        print "Latest version is already installed"
        pass
    else:

        from lmts_downloader import downloader
        downloader(lmts_file_url, f_name)

if __name__ == "__main__":
    main()
