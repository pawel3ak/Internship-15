# -*- coding: utf-8 -*-
'''
:author: Pawel Tarsa
:contact: tarsa.pawel@nokia.com
'''

__author__ = 'tarsa'
__copyright__ = 'Copyright 2015, Nokia'
__version__ = '2015-07-7'
__maintainer__ = 'tarsa Pawel Tarsa'
__email__ = 'tarsa.pawel@nokia.com'

import os
import sys
import atexit
import re
import subprocess
import time
from shlex import split

EMSS_CLOUD_DEFAULT_HOST = '10.0.1.1'
EMSS_CLOUD_DEFAULT_PORT = 4001

from ta_emss.emssexceptions.EmssExceptions import ErrUteEmssTimeout
import time
try:
    import pexpect
except ImportError:
    sys.stderr.write("You do not have 'pexpect' installed. \n")
    sys.stderr.write('On linux you need the "python-pexpect" package \n')
    exit(1)


class EmssimProcessStarter(object):

    def __init__(self, host, port, which_emss=1, timeout=30):
        self.setup_emss(which_emss=which_emss)
        #add here asserts for host and port should not be None? I think that it is art for art - not neccessary
        while not self._is_cloud_host_reachable() and timeout > 0:
            timeout -= 2
            time.sleep(2)
        time.sleep(30)   # let EMSS exchange data with eNB
        if timeout <= 0:
            raise ErrUteEmssTimeout()

    def setup_emss(self, which_emss=1):
        """
            Method starting EMSS processes.

            May be parametrized (if we work with HO setup) like:

            +----------------+-------------------+
            |              Examples              |
            +================+===================+
            |   start_emss      which_emss=1     |
            +----------------+-------------------+

        """
        if not self._is_fbox_running():
            self._start_localy_fbox_process()
        if not self._is_emss_running(which_emss=which_emss):
            flexi_process = self._move_to_flexi_user(user='flexi%s' % str(which_emss), pswd='flexi%s' % str(which_emss))
            self._start_emssim_as_choosed_user(process_with_logedin_user=flexi_process, user='flexi%s' % str(which_emss))
            self._check_if_emss_started(which_emss)
            #TODO add status-checking function

    def teardown_emss(self, which_emss=1):
        """
            Method stopping EMSS processes (both emss1 and emss2).

            May be parametrized (if we work with HO setup) like:

            +----------------+-------------------+
            |              Examples              |
            +================+===================+
            |   stop_emss    | which_emss = 1    |
            +----------------+-------------------+

        """
        kill_command = self._get_created_kill_command_from_given_pids(
            self._get_emss_start_process_pids(which_emss),
            self._get_fbox_dual_pid_if_started())
        self._execute_command(command=kill_command)

    def recover_emss_connection(self, which_emss=1):
        """
            Method which recover choosed EMSS session.
            Just kill and start choosed EMSS session.

            May be parametrized (if we work with HO setup) like:

            +----------------+-------------------------+
            |              Examples                    |
            +================+=========================+
            | recover_emss_connection | which_emss = 1 |
            +----------------+-------------------------+

        """
        self.teardown_emss(which_emss=which_emss)
        self.setup_emss(which_emss=which_emss)

    def _is_cloud_host_reachable(self):
        try:
            nmap_cmd = pexpect.spawn(command="nmap -p %d %s" % (EMSS_CLOUD_DEFAULT_PORT, EMSS_CLOUD_DEFAULT_HOST))
            match_index = nmap_cmd.expect([".*open.*", '.*closed.*', '.*filtered.*', '.*unfiltered.*', pexpect.EOF])
        except pexpect.TIMEOUT as err:
            print 'Timeouted: %s' % err.message.split('\n', 1)[0]
        if match_index == 0:
            return True
        else:
            return False

    def _all_done(self):
        print "Emss process start and killed without problems! Bye!"

    def _is_fbox_running(self):
        if self._get_fbox_dual_pid_if_started() == []:
            return False
        else:
            return True

    def _is_emss_running(self, which_emss=1):
        if self._get_emss_start_process_pids(which_emss) == []:
            return False
        else:
            return True

    def _check_if_emss_started(self, which_emss):
        emss_processes_pids = self._get_fbox_dual_pid_if_started()
        try:
            emss_processes_pids += self._get_emss_start_process_pids(which_emss)
        except Exception:
            print "FBOX_DUAL process does not exist\n"

    def _open_and_get_log_file(self, path_fo_log_file='/home/ute/emss_setup.log'):
        return open(path_fo_log_file, 'a+')

    def _move_to_flexi_user(self, user='flexi1', pswd='flexi1'):
        login_command = "sudo login %s" % user
        login_process = pexpect.spawn(login_command,
                                      logfile=self._open_and_get_log_file())
        login_process.expect("Password:")
        login_process.sendline(pswd)
        match_index = login_process.expect(["Login incorrect",
                                            pexpect.TIMEOUT,
                                            ".+%s" % user],
                                           timeout=5)
        if match_index == 0:
            sys.stderr.write("Login failed. Please check mocked in \
            _move_to_flexi_user credentials or contact with Pawel Tarsa\n")
            raise Exception
        elif match_index == 1:
            sys.stderr.write("Command timeout. Could not move to %s user! \
            It can be environment issue.\n" % user)
            raise Exception
        elif match_index == 2:
            if self._is_login_succeed(login_process, user):
                sys.stdout.write("Login as %s succeed\n" % user)
            return login_process

    def _is_login_succeed(self, process, user):
        process.sendline("whoami")
        match_index = process.expect(['.+%s' % user,
                                      pexpect.TIMEOUT],
                                     timeout=0.1)
        if match_index == 0:
            return True
        return False

    def _start_localy_fbox_process(self, path_to_folder_with_fbox_dual_file='/opt/emssim/proxy'):
        os.chdir(path_to_folder_with_fbox_dual_file)
        assert pexpect.run('pwd')[:-2] == path_to_folder_with_fbox_dual_file,\
            'Wrong localization! fbox_dual.pl has to starting from /opt/emssim/proxy/ folder!'

        start_fbox_process = pexpect.spawn("perl fbox_dual.pl",
                                           logfile=self._open_and_get_log_file())
        match_index = start_fbox_process.expect([".+FBOX \[v\d+.\d+\] STARTED",
                                                 pexpect.TIMEOUT,
                                                 pexpect.EOF],
                                                timeout=10)
        if match_index == 0:
            print "fbox_dual.pl started. "
        elif match_index == 1:
            print "Starting fbox_dual.pl failed! This may be environmental issue. " \
                  "Please check logs [%s]" % 'name_of_file - in constructor'
        elif match_index == 2:
            print("FBOX is probably already started.")
        return start_fbox_process

    def _get_fbox_dual_pid_if_started(self):
        fbox_dual_pid = re.findall("(\d{1,5})",
                                   self._get_specyfic_proceses_id(name_of_process='fbox'))
        return fbox_dual_pid[:1]

    def _get_emss_start_process_pids(self, which_emss):
        user = "flexi%s" % str(which_emss)
        list_of_START_EMSS_process_pids = re.findall("(\d{1,5})",
                                                     self._get_specyfic_proceses_id(name_of_process='fbox', effective_uid=user))
        return list_of_START_EMSS_process_pids

    def _get_created_kill_command_from_given_pids(self, *args):
        assert len(args) != 0, 'You don not give any process ID to %s method' % \
                               self._get_created_kill_command_from_given_pids.__name__
        kill_command = "sudo kill -9 "
        for given_list_of_pids in args:
            for pid in given_list_of_pids:
                kill_command += str(pid) + ' '
        return kill_command

    def _execute_command(self, command):
        out, err = subprocess.Popen(split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        self._verify_kill_command_status(stdout=out, stderr=err)

    def _verify_kill_command_status(self, stdout, stderr):
        print 'stdout' + stdout + "\nstderr: " + stderr
        if stdout == '' and stderr == '':
            print("EMSS killed correctly")
        if re.match("kill: invalid option -- \'9\'.*", stderr):
            print("EMSS cannot be killed. It can be simply not work. "
                  "To verify what is the issue please see log file.")
            with self._open_and_get_log_file() as log_file:
                pass  # maybe better use logging module? how to verify what other cases can be here?

    def _start_emssim_as_choosed_user(self, process_with_logedin_user, user='', dir_with_logs='/home/ute/emss_logs', log_on=True):
        print "\n In start_emssim_as_chosed_user method\n"
        if log_on:
            process_with_logedin_user.sendline("screen ./start")  # -LOG_FILE %" % )  # ./start ....-LOG_FILE ./mylog.txt
        match_index = process_with_logedin_user.expect(["\d{2}\:\d{2}\:\d{2}.+|Established Trace TCP-IP server.+", "Could not establish BTSOM "
                                                                                                                   "connection for BTS"])
        if match_index == 0:
            sys.stdout.write("EMSS started as %s user!\n" % user)
        elif match_index == 1:
            sys.stdout.write("EMSS is already started!\n")
        return process_with_logedin_user

    def _get_process_info(self):
        return pexpect.run('ps -ef')

    def _get_specyfic_proceses_id(self, name_of_process, effective_uid=None):
        if effective_uid:
            return pexpect.run('pgrep -f %s -U %s' % (name_of_process, effective_uid))
        else:
            return pexpect.run('pgrep -f %s' % name_of_process)


'''
ute@IAV-KRA-TL172:/home/emssim/proxy$ perl fbox_dual.pl

********************************************
* Starting FBOX [v1.5] ...
* For help use "-h" option
********************************************
* Insecure Flexi Port: 8002,
* Secure Flexi Port:   8003,
* EMSS Port:       8060,
* Diag port:       8061
Cannot open log file: ./fbox-IAV-KRA-TL172-8060.log
Running FBOX without logging to file
2015-06-17 13:56:52 ********************************************
2015-06-17 13:56:52 * FBOX [v1.5] STARTED
2015-06-17 13:56:52 * EMSS Port: 8060
2015-06-17 13:56:52 * Flexi Insecure Port: 8002
2015-06-17 13:56:52 * Flexi Secure Port: 8003
2015-06-17 13:56:52 * Diag port: 8061
2015-06-17 13:56:52 ********************************************


ute@IAV-KRA-TL172:/home/emssim/proxy$ perl fbox_dual.pl

********************************************
* Starting FBOX [v1.5] ...
* For help use "-h" option
********************************************
* Insecure Flexi Port: 8002,
* Secure Flexi Port:   8003,
* EMSS Port:       8060,
* Diag port:       8061
ERROR: FBOX couldn't start TCP socket (Flexi insecure) on port 8002. (Address already in use)
IO::Socket::INET: Address already in use...propagated at fbox_dual.pl line 119.
ute@IAV-KRA-TL172:/home/emssim/proxy$

#############################################################################

flexi1@IAV-KRA-TL172:~$ ./start
13:57:13      |Using EMS CORE Release   'release_7_0_latest'
13:57:13      |Using SIM Release    'release_7_0_latest'
13:57:13      |Using SNMP Release       'release_7_0_latest'
13:57:13      |Using User Path '/home/emssim/privates/flexi_fbox/'
13:57:13      |Set screen detail level to 3
13:57:13      |Creating Manager...
13:57:13      |***************************************************
13:57:13      |****************** EMS Simulator ******************
13:57:13      |***************************************************
13:57:13      |Established TCP-IP server at IAV-KRA-TL172.lab0.krk-lab.nsn-rdnet.net:7001
13:57:13      |Established TCP-IP server at IAV-KRA-TL172.lab0.krk-lab.nsn-rdnet.net:4001
13:57:14      |Created BTS
13:57:14      |Connecting to Flexi Proxy 10.0.1.1:8060
13:57:14      |Connected.
13:57:14 FBOX     |Received Flexi IP: 10.0.1.2
13:57:14      |+ Alarms for BTS 1 will be saved in a file:
13:57:14      | /home/flexi1/ALARM_SUMMARY/Alarms-MRBTS-1.log
13:57:14      |Established Trace TCP-IP server at localhost:49001
>



flexi1@IAV-KRA-TL172:~$ ./start
13:55:54      |Using EMS CORE Release   'release_7_0_latest'
13:55:54      |Using SIM Release    'release_7_0_latest'
13:55:54      |Using SNMP Release       'release_7_0_latest'
13:55:54      |Using User Path '/home/emssim/privates/flexi_fbox/'
13:55:54      |Set screen detail level to 3
13:55:54      |Creating Manager...
13:55:54      |***************************************************
13:55:54      |****************** EMS Simulator ******************
13:55:54      |***************************************************
13:55:54      |ERROR: Unable to bind socket to port 7001
13:55:54      |ERROR: Unable to bind socket to port 4001
13:55:54      |Created BTS
13:55:54      |Connecting to Flexi Proxy 10.0.1.1:8060
13:55:54      |Connected.
13:55:54      |ERROR: Flexi flexi1 is already taken by:
13:55:54      |  User: flexi1
13:55:54      |  Host: 10.0.1.1
13:55:54      |  PID: 7663
13:55:54      |
13:55:54      |Could not establish BTSOM connection for BTS flexi1
>

'''
