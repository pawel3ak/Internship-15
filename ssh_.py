# -*- coding: utf-8 -*-
"""
:created on: '6/8/15'

:copyright: NSN
:author: Pawel Nogiec
:contact: pawel.nogiec@nsn.com
"""

import pexpect
import time

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

