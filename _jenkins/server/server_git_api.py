import os
import pexpect
import re
import paramiko
import time

path = '/home/ute/PycharmProjects/projekty/Internship-15'
def git_action(ssh_process, command):
    exepcted_matches_list = ['Writing objects:.*done', 'Unpacking objects:.*done', 'no changes added to commit',
               'Aborting commit', 'fatal', '.*up-to-date', 'Password.*:', pexpect.EOF, pexpect.TIMEOUT]

    ssh_process.sendline(command)
    while True:
        match = ssh_process.expect(exepcted_matches_list, timeout=1)
        if match == 0:
            return True
        elif match == 1:
            return True
        elif match == 2:
            return "Commit failure - no changes"
        elif match == 3:
            return "Commit failure - aborting"
        elif match == 4:
            return "Fatal failure - no file to add"
        elif match == 5:
            return True
        elif match == 6:
            passwd =raw_input("Enter password\n")
            ssh_process.sendline(passwd)
        elif match == 7:
            return "Unknown failure"


def git_launch(TL_address, file_info, pull_only):
    ssh_process = ssh_for_git(TL_address)
    #git pull
    result = git_action(ssh_process, 'git pull')
    if not result == True: return result
    if pull_only == True: return True
    #git add
    result = git_action('git add {}'.format(os.path.join(file_info[0],file_info[1])))
    if not result == True: return result
    #git commit
    result = git_action('git commit "Removing tag from file "{}""'.format(file_info[1]))
    if not result == True: return result
    #git push
    result = git_action('git push')
    if not result == True: return result
    return True


def ssh_for_git(TL_address):
    ssh_command = "ssh {user}@{host}".format(user="ute", host=TL_address)
    ssh_process = pexpect.spawn(ssh_command)
    match = ssh_process.expect(["password:", pexpect.EOF, pexpect.TIMEOUT], timeout=1)
    if match == 0:
        time.sleep(0.1)
        ssh_process.sendline('ute')
        time.sleep(2)
    ssh_process.sendline('cd /home/ute/auto/ruff_scripts/')
    match = ssh_process.expect(['.*cd.*',pexpect.EOF, pexpect.TIMEOUT], timeout=1)
    if match == 0:
        print ssh_process.before
    return ssh_process


    # client = paramiko.SSHClient()
    # client.load_system_host_keys()
    # client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # client.connect(TL_address, username='ute', password='ute')
    # return client

git_launch('wmp-tl99.lab0.krk-lab.nsn-rdnet.net')
