# -*- coding: utf-8 -*-
"""
:created on: '6/8/15'

:author: Damian Papiez
"""

import pexpect
import sys
from time import sleep

def _lmts_upgrade ():
    #1 LMTS-executor start
    child_bash = pexpect.spawn("/bin/bash")
    child_bash.sendline("sudo /etc/init.d/lmts-executor start")
    try:
        child_bash.expect("Starting up LMTS Executor:")
        i = child_bash.expect(["\.", "failed", pexpect.TIMEOUT])
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - starting up LMTS Executor"
        sys.exit(1)
    if i == 1:
        child_bash.sendline("sudo /etc/init.d/lmts-executor stop")
        sleep(1)
        child_bash.sendline("sudo /etc/init.d/lmts-executor start")
        try:
            child_bash.expect("Starting up LMTS Executor:")
            i = child_bash.expect(["\.", "failed"])
        except pexpect.TIMEOUT:
            print "pexpect.TIMEOUT - starting up LMTS Executor"
            sys.exit(1)
        if i == 1:
            print "LMTS-executor start fail"
            sys.exit(1);
    sleep (2)

    #2 LMTS-trace start
    child_bash.sendline("sudo /etc/init.d/lmts-trace start")
    try:
        child_bash.expect("Starting up LMTS trace")
        i = child_bash.expect(["\.", "failed", "process already running"])
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - starting up LMTS Executor"
        sys.exit(2)
    if i == 1:
        print "LMTS-trace start fail"
        sys.exit(2);
    sleep (2)

    #3 start telnet connection
    child_bash.sendline("telnet 0 1234")
    try:
        child_bash.expect("Connected")
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - telnet connection"
        sys.exit(3)

    #4 config update
    child_bash.sendline("config update")
    try:
        child_bash.expect("New configuration applied")
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - config update"
        sys.exit(4)

    #5 config remote reload
    child_bash.sendline("config remote reload")
    sleep(1)
    child_bash.sendline("config remote reload")#take long to execute
    sleep(1)
    try:
        child_bash.expect("(no)? yes", timeout=400)
        sleep(1)
        child_bash.expect("RETURN CODE: 0", timeout=200)
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - config remote reload"
        sys.exit(5)

    #6 config ue reload
    child_bash.sendline("config ue reload")
    try:
        child_bash.expect("UE data reloaded")
        sleep(1)
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - config ue reload"
        sys.exit(6)


    #7 config loopback
    child_bash.sendline("config loopback")
    try:
        child_bash.expect("Looback config successfully applied")
        sleep(1)
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - config ue reload"
        sys.exit(7)

    #8 config remote update
    child_bash.sendline("condig remote update")
    '''
    try:
        child_bash.expect(" ", timeout=)
        sleep(1)
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - config ue reload"
        sys.exit(8)
    '''


if __name__ == "__main__":
    _lmts_upgrade()
