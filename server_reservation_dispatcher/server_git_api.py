import os
import pexpect
import re
import paramiko
import time
import logging

# create logger
logger = logging.getLogger("server." + __name__)
#################################################
################ temporary ######################
from utilities.logger_config import config_logger
config_logger(logger, 'server_config.cfg')
#################################################

path = '/home/ute/PycharmProjects/projekty/Internship-15'


def git_action(ssh_process, command):
    exepcted_matches_list = ['Writing objects:.*done', 'Unpacking objects:.*done', 'no changes added to commit',
               'Aborting commit', 'fatal', '.*up-to-date', 'Password.*:', pexpect.EOF, pexpect.TIMEOUT]
    # ssh_process.expect(['\r\n',pexpect.EOF,pexpect.TIMEOUT], timeout=10)
    # ssh_process.sendline('pwd')
    # print ssh_process.before
    # print ssh_process.after
    # print ssh_process
    while True:
        match = ssh_process.expect(exepcted_matches_list, timeout=1)
        if match == 0:
            return True
        elif match == 1:
            return True
        elif match == 2:
            logger.error("Commit failure - no changes")
            # non empty string bool value is True and we cannot break git_launch function
            # if something goes wrong
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
            # passwd =raw_input("Enter password\n")
            passwd = ""
            ssh_process.sendline(passwd)
        elif match == 7:
            logger.error("Unknown failure")
            return False
        else:
            logger.error("I don't know what's happened")
            print ssh_process.before
            return None


def git_launch(TL_address, file_info, pull_only=True):
    print "pull only = ", pull_only # TODO remove
    ssh_process = ssh_for_git(TL_address)
    logger.debug("ssh_process = {}".format(ssh_process))

    # git pull
    result = git_action(ssh_process, 'git pull')
    print "result = ", result
    if not result:
        return False
    if pull_only:
        return True
    # print 'git add {}'.format(os.path.join(file_info[0],file_info[1]))
    # print 'git commit "Removing tag from file "{}""'.format(file_info[1])
    #git add
    # result = git_action('git add {}'.format(os.path.
    # join(file_info[0],file_info[1])))
    # if not result == True: return result
    # git commit
    # result = git_action('git commit "Removing tag from file "{}""'.format(file_info[1]))
    # if not result == True: return result
    # git push
    # result = git_action('git push')
    # if not result == True: return result
    return True


def ssh_for_git(TL_address):
    ssh_command = "ssh {user}@{host}".format(user="ute", host=TL_address)
    logger.info(ssh_command)
    ssh_process = pexpect.spawn(ssh_command)
    match = ssh_process.expect(["password:", pexpect.EOF, pexpect.TIMEOUT], timeout=3)
    if match == 0:
        time.sleep(0.1)
        ssh_process.sendline('ute')
        time.sleep(2)
    # print ssh_process.before
    # print ssh_process.after
    ssh_process.sendline('cd /home/ute/auto/ruff_scripts/')
    match = ssh_process.expect(['.*cd.*',pexpect.EOF, pexpect.TIMEOUT])
    if match == 0:
        print ssh_process.before
        # print ssh_process.after
    # elif match == 1:
    #     print ssh_process.before
    #     print ssh_process.after
    # elif match == 2:
    #     print ssh_process.before
    #     print ssh_process.after
    # ssh_process.sendline("ls")
    # print ssh_process.before
    # print ssh_process.after
    return ssh_process


    # client = paramiko.SSHClient()
    # client.load_system_host_keys()
    # client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # client.connect(TL_address, username='ute', password='ute')
    # return client

if __name__ == "__main__":
    git_launch('localhost', file_info=None, pull_only=True)
