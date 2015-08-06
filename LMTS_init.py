# -*- coding: utf-8 -*-
"""
:created on: '6/8/15'

:author: Damian Papiez
"""

import pexpect
import sys
from time import sleep

#LMTS-executor start
child_bash = pexpect.spawn("/bin/bash")
child_bash.sendline("sudo /etc/init.d/lmts-executor start")
try:
    child_bash.expect("Starting up LMTS Executor:")
    i = child_bash.expect(["\.", "failed", pexpect.TIMEOUT])
except pexpect.TIMEOUT:
    print "pexpect.TIMEOUT - starting up LMTS Executor"
    sys.exit(0)
if i == 1:
    child_bash.sendline("sudo /etc/init.d/lmts-executor stop")
    sleep(1)
    child_bash.sendline("sudo /etc/init.d/lmts-executor start")
    try:
        child_bash.expect("Starting up LMTS Executor:")
        i = child_bash.expect(["\.", "failed"])
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - starting up LMTS Executor"
        sys.exit(0)
    if i == 1:
        print "LMTS-executor start fail"
        sys.exit(0);
sleep (2)

#LMTS-trace start
child_bash.sendline("sudo /etc/init.d/lmts-trace start")
try:
    child_bash.expect("Starting up LMTS trace")
    i = child_bash.expect(["\.", "failed", "process already running"])
except pexpect.TIMEOUT:
    print "pexpect.TIMEOUT - starting up LMTS Executor"
    sys.exit(0)
if i == 1:
    print "LMTS-trace start fail"
    sys.exit(0);
sleep (2)

#start telnet connection
child_bash.sendline("telnet 0 1234")
try:
    child_bash.expect("Connected")
    child_bash.expect("LTE-LMTS>")
except pexpect.TIMEOUT:
    print "pexpect.TIMEOUT - telnet connection"
    sys.exit(0)

#config update
child_bash.sendline("config update")
try:
    child_bash.expect("New configuration applied")
    child_bash.expect("LTE-LMTS>")
except pexpect.TIMEOUT:
    print "pexpect.TIMEOUT - config update"
    sys.exit(0)
