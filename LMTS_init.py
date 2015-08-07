# -*- coding: utf-8 -*-
"""
:created on: '6/8/15'

:author: Damian Papiez
"""

import pexpect
from time import sleep

def _lmts_upgrade ():
    #1 LMTS-executor start
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
    sleep (2)

    #2 LMTS-trace start
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
    sleep (2)

    #3 start telnet connection
    print "start telnet connection"
    child_bash.sendline("telnet 0 1234")
    try:
        child_bash.expect("Connected")
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - telnet connection"
        return 3

    #4 config update
    print "config update"
    child_bash.sendline("config update")
    try:
        child_bash.expect("New configuration applied")
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - config update"
        return 4

    #5 config remote reload
    print "config remote reload - can take few minutes"
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
        return 5

    #6 config ue reload
    print "config ue reload"
    child_bash.sendline("config ue reload")
    try:
        child_bash.expect("UE data reloaded")
        sleep(1)
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - config ue reload"
        return 6


    #7 config loopback
    print "config loopback"
    child_bash.sendline("config loopback")
    try:
        child_bash.expect("Looback config successfully applied")
        sleep(1)
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - config loopback"
        return 7

    #8 config loopback apply tgrs
    print "config loopback apply tgrs"
    child_bash.sendline("config loopback apply tgrs")
    try:
        #child_bash.expect("Looback config successfully applied")
        sleep(1)
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - config loopback apply tgrs"
        return 8

    #9 cm server start
    print "cm server start"
    child_bash.sendline("cm server start")
    try:
        #child_bash.expect(" ")
        sleep(1)
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - cm server start"
        return 9

    #10 config remote update
    print "config remote update"
    child_bash.sendline("condig remote update")
    try:
        #child_bash.expect(" ")
        sleep(1)
        child_bash.expect("LTE-LMTS>")
    except pexpect.TIMEOUT:
        print "pexpect.TIMEOUT - config remote update"
        return 10
    print "all done"


if __name__ == "__main__":
    print _lmts_upgrade()
