# -*- coding: utf-8 -*-
"""
:copyright: Nokia
:author: Pawel Tarsa
:contact: tarsa@nsn.com
"""
import pexpect
import sys


class DebianService(object):

    def __init__(self):
        pass

    def _move_to_given_user_and_return_this_process(self, user, pswd=None, logfile=None):
        if user == "root":
            login_command = "sudo su"
            login_process = pexpect.spawn(login_command, logfile=logfile, timeout=600)
            match_index = login_process.expect(["root@.*", pexpect.TIMEOUT])
        else:
            login_command = "sudo login %s" % user
            login_process = pexpect.spawn(login_command, logfile=logfile)
            login_process.expect("Password:")
            login_process.sendline(pswd)
            match_index = login_process.expect([".+%s" % user, "Login incorrect", pexpect.TIMEOUT], timeout=5)
        if match_index == 0:
            if self._is_login_succeed(login_process, user):
                sys.stdout.write("Login as %s succeed\n" % user)
            return login_process
        elif match_index == 1:
            sys.stderr.write("Login failed. Please check mocked in \
            _move_to_given_user credentials or contact with Pawel Tarsa\n")
            raise Exception
        elif match_index == 2:
            sys.stderr.write("Command timeout. Could not move to %s user! \
            It can be environment issue.\n" % user)
            raise Exception

    def _is_login_succeed(self, process, user):
        process.sendline("whoami")
        match_index = process.expect(['.+%s' % user, pexpect.TIMEOUT], timeout=0.1)
        if match_index == 0:
            return True
        return False
