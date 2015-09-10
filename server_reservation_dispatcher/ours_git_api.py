# -*- coding: utf-8 -*-
"""
:created on: '11/08/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nokia.com
"""

import pexpect
import time
import logging


# create logger
logger = logging.getLogger("server." + __name__)


def git_action(ssh_process, command, comment = None):
    if comment:
        command = '{} -m "{}"'.format(command,comment)

    exepcted_matches_list = ['Writing objects:.*done',#0
                             'Unpacking objects:.*done',#1
                             'no changes added to commit',#2
                             'Aborting commit',#3
                             'fatal',#4
                             '.*up-to-date',#5
                             'Password.*:',#6
                             '.*~//PycharmProjects/projekty/Internship-15.*',#7
                             '.*{}.*'.format(comment),#8
                             pexpect.EOF,#8
                             pexpect.TIMEOUT]#9
    ssh_process.sendline(command)
    while True:
        match = ssh_process.expect(exepcted_matches_list, timeout=1)
        if match == 0:
            return True
        elif match == 1:
            return True
        elif match == 2:
            logger.error("Commit failure - no changes")
            return False
        elif match == 3:
            logger.error("Commit failure - aborting")
            return False
        elif match == 4:
            logger.error("Fatal failure - no file to add")
            return False
        elif match == 5:
            return True
        elif match == 6:
            passwd = "Flexi1234"
            ssh_process.sendline(passwd)
        elif match == 7:
            return True
        elif match == 8:
            return True
        elif match == 9:
            pass


def git_launch(TL_address, path, pull_only=True):
    ssh_process = ssh_for_git(TL_address, path)
    # git pull
    result = git_action(ssh_process, 'git pull')
    if not result:
        return False
    if pull_only:
        return True
    #git add
    ssh_process.sendline('git add {}'.format(path))
    #git commit
    result = git_action(ssh_process, 'git commit', 'Testing git_api')
    if not result:
        return False
    # git push
    result = git_action(ssh_process, 'git push')
    if not result:
        return False
    return True


def ssh_for_git(TL_address, path):
    ssh_command = "ssh {user}@{host}".format(user="ute", host=TL_address)
    logger.info(ssh_command)
    ssh_process = pexpect.spawn(ssh_command)
    while True:
        match = ssh_process.expect(["password:", pexpect.EOF, pexpect.TIMEOUT], timeout=1)
        if match == 0:
            time.sleep(0.2)
            ssh_process.sendline('ute')
            time.sleep(2)
        else:
            break
    ssh_process.sendline('cd {}'.format(path))
    while True:
        match = ssh_process.expect(['.*cd.*',pexpect.EOF, pexpect.TIMEOUT], timeout=1)
        if match == 0:
            return ssh_process


# if __name__ == "__main__":
#     path = "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTEtest"
#     print git_launch('localhost', path, pull_only=False)
