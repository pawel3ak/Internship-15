# -*- coding: utf-8 -*-
"""
:created on: '6/8/15'

:copyright: NSN
:author: Damian Papiez
"""

__author__ = 'ute'

import pexpect
import sys
from time import sleep

child_bash = pexpect.spawn("/bin/bash")
child_bash.sendline("sudo /etc/init.d/lmts-executor start")
child_bash.expect("Starting up LMTS Executor:")
i = child_bash.expect(["\.", "failed", pexpect.TIMEOUT])

if i == 1:
    child_bash.sendline("sudo /etc/init.d/lmts-executor stop")
    sleep(1)
    child_bash.sendline("sudo /etc/init.d/lmts-executor start")
    child_bash.expect("Starting up LMTS Executor:")
    i = child_bash.expect(["\.", "failed", pexpect.TIMEOUT])
    if i == 1:
        print "LMTS-executor start fail"
        sys.exit(0);
    elif i == 2:
        print "Time out!"
        sys.exit(0);
elif i == 2:
    print "Time out!"
    sys.exit(0);


