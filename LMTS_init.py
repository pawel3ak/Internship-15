# -*- coding: utf-8 -*-
"""
:created on: '6/8/15'

:copyright: NSN
:author: Damian Papiez
"""

import pexpect
import sys
from time import sleep

child_bash = pexpect.spawn("/bin/bash")
'''
child_bash.sendline("sudo /etc/init.d/lmts-executor stop")
child_bash.expect("\n")
child_bash.expect("\n")
child_bash.expect("\n")
print child_bash.before
'''
child_bash.sendline("sudo /etc/init.d/lmts-executor start")
child_bash.expect("Starting up LMTS Executor:")
i = child_bash.expect(["\.", "failed", pexpect.TIMEOUT])

if i == 1:
    print "failed"
elif i == 2:
    print "Time out!"

