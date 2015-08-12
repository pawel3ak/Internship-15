# -*- coding: utf-8 -*-
"""
:created on: '6/8/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""

import pexpect
from time import sleep


def _wait_for_server_response():
    print "waiting for server response"
    pinging_bash = pexpect.spawn("/bin/bash")
    while True:
        sleep(1)
        pinging_bash.sendline("ping -c 1 10.60.0.11")
        control_output = pinging_bash.expect(["bytes from 10.60.0.11", "Destination Host Unreachable"])
        if not control_output == 0:
            pass
        else:
            pinging_bash.sendline("exit")
            return 0

def _lmts_upgrade():

    # 1 LMTS-executor start
    print "LMTS-executor"
    child_bash = pexpect.spawn("/bin/bash")
    child_bash.sendline("sudo /etc/init.d/lmts-executor start")
    try:
        child_bash.expect("Starting up LMTS Executor:")
        i = child_bash.expect(["\.", "failed", pexpect.TIMEOUT])
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - starting up LMTS Executor"
        return 1
    if i == 1:
        child_bash.sendline("sudo /etc/init.d/lmts-executor stop")
        sleep(2)
        child_bash.sendline("sudo /etc/init.d/lmts-executor start")
        try:
            child_bash.expect("Starting up LMTS Executor:")
            i = child_bash.expect(["\.", "failed"])
        except pexpect.TIMEOUT:
            print "pexpect.TIMEOUT - starting up LMTS Executor"
            return 1
        if i == 1:
            print "LMTS-executor start fail"
            return 1
    sleep(2)

    # 2 LMTS-trace start
    print "LMTS-trace"
    child_bash.sendline("sudo /etc/init.d/lmts-trace start")
    try:
        child_bash.expect("Starting up LMTS trace")
        i = child_bash.expect(["\.", "failed", "process already running"])
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - starting up LMTS Executor"
        return 2
    if i == 1:
        print "LMTS-trace start fail"
        return 2
    sleep(2)

    # 3 start telnet connection
    print "start telnet connection"
    child_bash.sendline("telnet 0 1234")
    try:
        child_bash.expect("Connected")
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - telnet connection"
        return 3

    # 4 config update
    print "config update"
    child_bash.sendline("config update")
    try:
        child_bash.expect("New configuration applied")
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - config update"
        return 4

    # 5 config remote reload
    print "config remote reload - can take few minutes"
    child_bash.sendline("config remote reload")
    sleep(1)
    child_bash.sendline("config remote reload")  # take long to execute
    sleep(1)
    try:
        child_bash.expect("(no)? yes", timeout=500)
        sleep(1)
        child_bash.expect("RETURN CODE: 0", timeout=200)
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - config remote reload"
        return 5

    # 6 config ue reload
    print "config ue reload"
    child_bash.sendline("config ue reload")
    try:
        child_bash.expect("UE data reloaded")
        sleep(1)
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - config ue reload"
        return 6

    # 7 config loopback apply tgrs
    print "config loopback apply tgrs"
    child_bash.sendline("config loopback apply tgrs")
    try:
        child_bash.expect("Looback config successfully applied")
        sleep(1)
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - config loopback apply tgrs"
        return 7

    # 8 cm server start
    print "cm server start"
    child_bash.sendline("cm server start")
    try:
        child_bash.expect("Loopback server started")
        sleep(1)
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - cm server start"
        return 8

    # 9 config remote update
    print 99
    _wait_for_server_response()
    print "config remote update"
    child_bash.sendline("condig remote update")
    try:
        control_output = child_bash.expect(["CTRL-1: COMMAND: /sbin/reload", "Error connecting to CTRL-1"], timeout=200)
        if control_output == 1:
            #sleep(30)
            print "retry config remote update"
            child_bash.sendline("condig remote update")
            sleep(1)
            control_output = child_bash.expect(["CTRL-1: COMMAND: /sbin/reload", "Error connecting to CTRL-1"], timeout=200)
            if control_output == 1:
                print "Error connecting to CTRL-1"
                return 10
        sleep(1)
        child_bash.expect("RETURN CODE: 0")
        sleep(1)
        child_bash.expect("LTE-LMTS>", timeout=200)
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - config remote update"
        return 10

    print "all done"
    child_bash.sendline("exit")


if __name__ == "__main__":
    print _lmts_upgrade()
