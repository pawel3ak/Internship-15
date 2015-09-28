# -*- coding: utf-8 -*-
"""
:copyright: Nokia
:author: Pawel Tarsa
:contact: tarsa@nsn.com
"""
import os
import paramiko
import pexpect
import pprint
import sys
from time import sleep
from LMTS_init.debian_service import DebianService


class LmtsManager(DebianService):

    MISSING_PACKAGES = ["blt", "fonts-lyx", "lib32readline5", "libconfig-inifiles-perl", "python-apsw", "python-dateutil", "python-matplotlib",
                        "python-matplotlib-data", "python-pexpect", "python-pyparsing", "python-tk", "python-tz", "python-wxgtk2.8", "python-wxversion", "vsftpd"]

    def __init__(self):
        self.telnet_executor = None
        self._lmts_package_name = None
        self._path_to_folder_with_package = None  # to re-thinking
        self.tgr_ips_list = None
        self.tgrs_available = False

    def initialize_lmts(self):
        '''
        Method which fully initialize LMTS-device.
        :return: None
        '''
        self._extend_permissions_to_lmts()
        if not self._is_lmts_executor_started():
            sys.stderr.write("LMTS not started")
            self._start_lmts_executor()
            sys.stderr.write("LMTS executor started")
            self._start_lmts_trace()
            sys.stderr.write("LMTS trace started")
        self._connect_to_LMTS_executor()
        self._update_lmts_configuration()
        self._reload_lmts_ues()
        self._configure_loopback()
        self._perform_remote_update()

    def install_lmts_package_via_dpkg(self, path_to_package):
        '''
        :param path_to_package: e.g. /home/ute/lmts/lte-lmts_8.0.1.01-1.06_amd64.deb
        :return:
        '''
        self._install_all_missing_dependencies()
        install_lmts_executor = pexpect.spawn("sudo dpkg -i %s" % path_to_package, logfile=self._open_and_get_logging_file())
        match_index = install_lmts_executor.expect([".*Starting NTP server: ntpd.", ".*Errors were encountered while processing:.+",
                                                    ".*dpkg: error: dpkg status database is locked by another process.*", pexpect.TIMEOUT,
                                                    pexpect.EOF], timeout=500)
        print(install_lmts_executor.before)
        print(install_lmts_executor.after)
        if match_index == 0:
            print("Everything goes fine, LMTS installed correctly\n")
        elif match_index == 1:
            print("During installation appear ERRORs. Please contact with Pawel Tarsa or Michal Kowalski\
             (Krakow Site, PL) and prepare logs from installation")
        elif match_index == 2:
            print(install_lmts_executor.before)
            pexpect.spawn("sudo rm /var/lib/dpkg/lock; sudo dpkg --configure -a", logfile=self._open_and_get_logging_file())
            #  handle this situation better
        else:
            raise Exception

    def download_lmts_package_from_server(self, server_ip="10.83.200.35", username="ltebox", password="Motorola", lmts_deb_pkg_name=None,
                                          path_to_folder_with_package="/home/ltebox/public_html/ute_packages/lmts/",
                                          path_to_local_lmts_folder="/home/ute/lmts"):
        """
        :param string hostname:
        :param string username:
        :param string password:
        :param string path_to_folder_with_package: path to remote resources same as local downloading folder
        :return: nothing
        :result: method to copy via sftp some files to mocked localization. It is important to give correct localization (with all folders existing)
        """
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(hostname=server_ip, username=username, password=password)
        self.ftp_client = self.ssh_client.open_sftp()
        # protection by non-existing folders
        self._is_existing_folder_in_remote_system(complete_path=path_to_folder_with_package)
        lmts_latest_build = self._get_latest_lmts_deb_pkg_name_available_in_remote_system(path_to_folder_with_package=path_to_folder_with_package)
        if not self._is_lmts_package_localy_available(path_to_folder_with_package=path_to_local_lmts_folder, lmts_latest_build=lmts_latest_build):
            self._create_given_folders_tree_if_not_exists(complete_path=path_to_local_lmts_folder)
            self.ftp_client.get(path_to_folder_with_package + r"/" + lmts_latest_build, path_to_local_lmts_folder+lmts_latest_build)

    def _is_lmts_package_localy_available(self, path_to_folder_with_package, lmts_latest_build):
        if "lmts" in os.listdir("/home/ute"):
            files_list = os.listdir(path_to_folder_with_package)
            if lmts_latest_build in files_list:
                print("LMTS_package is available localy\n")
                return True
        else:
            return False

    def _are_tgrs_reachable(self):
        self._parse_and_save_tgr_ips_from_lmts_ini_file()
        pprint.pprint(self.tgr_ips_list)
        for tgr_ip in self.tgr_ips_list:
            if (pexpect.spawn("ping {tgr_ip} -c 1".format(tgr_ip=tgr_ip), logfile=sys.stderr)).expect([".* 0% packet loss.*", ".*100% packet loss.*"], timeout=20) != 0:
                self.tgrs_available = False
                return False
        self.tgrs_available = True
        return True

    def _extend_permissions_to_lmts(self):
        print pexpect.run("sudo chmod 777 -R /usr/lmts/")

    def _start_lmts_executor(self):
        executor_starting_process = pexpect.spawn("sudo /etc/init.d/lmts-executor start", logfile=self._open_and_get_logging_file())
        try:
            match_index = executor_starting_process.expect([".*Starting up LMTS Executor:\..*", ".*Starting up LMTS Executor: failed.*", ".*Command not found.*", pexpect.TIMEOUT])
        except pexpect.TIMEOUT:
            print "pexpect.TIMEOUT - starting up LMTS Executor"
            return 1
        if match_index == 1:
            executor_starting_process.sendline("sudo /etc/init.d/lmts-executor stop")
            sleep(2)
            executor_starting_process.sendline("sudo /etc/init.d/lmts-executor start")
        try:
            match_index = executor_starting_process.expect([".*Starting up LMTS Executor:\..*", ".*Starting up LMTS Executor: failed.*", ".*Command not found.*", pexpect.TIMEOUT])
        except pexpect.TIMEOUT:
            print "pexpect.TIMEOUT - starting up LMTS Executor"
            return 1
        if match_index == 1:
            print "LMTS-executor start fail"
            return 1
        sleep(2)

    def _start_lmts_trace(self):
        trace_starting_process = pexpect.spawn("sudo /etc/init.d/lmts-trace start", logfile=self._open_and_get_logging_file())
        try:
            match_index = trace_starting_process.expect([".*Starting up LMTS trace :.", ".*Starting up LMTS trace :process already running.", ".*Command not found.*", pexpect.TIMEOUT])
        except pexpect.TIMEOUT:
            return 2
        if match_index == 1:
            print("LMTS trace already running\n")
        if match_index == 2:
            print("Command not found - lte-lmts may be not installed\n")
            return 2

    def _connect_to_LMTS_executor(self):
        self.telnet_executor = pexpect.spawn("telnet 0 1234", logfile=self._open_and_get_logging_file())
        try:
            match_index = self.telnet_executor.expect([".*LTE-LMTS>.*", ".*Connection refused"])
        except pexpect.TIMEOUT:
            print("Unable to connect with LMTS\n")
        if match_index == 3:
            print("Unable to connect with LMTS\n")
        sys.stderr.write("Connecting to lmts exec: "+self.telnet_executor.after+self.telnet_executor.before)  # TODO only for debugging

    def _is_lmts_executor_started(self):
        _telnet_executor = pexpect.spawn("telnet 0 1234", logfile=self._open_and_get_logging_file())
        try:
            match_index = _telnet_executor.expect([".*LTE-LMTS>.*", ".*Connection refused.*", pexpect.TIMEOUT])
        except pexpect.TIMEOUT:
            print("Executor not started!\n")
            return False
        if match_index == 0:
            return True

    def _reload_lmts_ues(self):
        self.telnet_executor.sendline("config ue reload")
        try:
            self.telnet_executor.expect(["UE data reloaded", pexpect.TIMEOUT])
            sys.stderr.write("\n\n\nConfigure UE Reload: "+self.telnet_executor.after+self.telnet_executor.before)  # TODO only for debugging
        except pexpect.TIMEOUT:
            print("Reloading UEs failed\n")

    def _update_lmts_configuration(self):
        self.telnet_executor.sendline("config update")
        try:
            self.telnet_executor.expect(["New configuration applied", pexpect.TIMEOUT])
            sys.stderr.write("\n\n\nConfig update: "+self.telnet_executor.after+self.telnet_executor.before)  # TODO only for debugging
        except pexpect.TIMEOUT:
            print("Configuration update failed\n")

    def _configure_loopback(self):
        sys.stderr.write("in configure loopback\n")
        if not self._are_tgrs_reachable():
            self.telnet_executor.sendline("config loopback apply tgrs")
            try:
                self.telnet_executor.expect(["Looback config successfully applied", ".*Error applying loopback config: ERROR: Looback config already applied.*", pexpect.TIMEOUT])
                sys.stderr.write("\n\n\n configuration loopback: "+self.telnet_executor.after+self.telnet_executor.before)  # TODO only for debugging
            except pexpect.TIMEOUT:
                print("pexpect.TIMEOUT - config loopback apply tgrs")
            sleep(1)
            self.telnet_executor.sendline("cm server start")
            try:
                match_index = self.telnet_executor.expect(["Loopback server started", "Loopback Server is already running.*"])
                sys.stderr.write("\n\n\n com server started: "+self.telnet_executor.after+self.telnet_executor.before)  # TODO only for debugging
            except:
                print self.telnet_executor.before
                print self.telnet_executor.after
                print("\nError connected with cm server starting")

    def _perform_remote_update(self):
        self.telnet_executor.sendline("config remote update")
        try:
            match_index = self.telnet_executor.expect([".*LTE-LMTS>.*", "Error connecting to CTRL-1"], timeout=200)
            if match_index == 1:
                print("Error in config remote configuration")
        except pexpect.TIMEOUT:
            print("Error in config remote configuration")

    def _parse_and_save_tgr_ips_from_lmts_ini_file(self, path_to_lmts_file="/usr/lmts/etc/lmts.ini"):
        """
        [tgr_1]
        ip_addr                     = 10.60.0.4                              < -- 1st interesting IP
        ss_ip_addr_pool             = 185.4.0.0/16
        ss_interface                = eth0
        side                        = SS
        password                    = emssim
        [tgr_2]
        ip_addr                     = 10.60.0.3                              < -- 2nd interesting IP
        ue_interface                = eth0
        side                        = MS
        password                    = emssim

        :return: ['10.60.0.4', '10.60.0.3']
        """
        searched_fragment_pattern = "\[tgr_\d\]\Wip_addr.+=.(\d+\.\d+\.\d+\.\d+)"
        with open(path_to_lmts_file, 'r') as lmts_config_file:
            data = lmts_config_file.read()
            import re
            self.tgr_ips_list = re.findall(searched_fragment_pattern, data)

    def _install_all_missing_dependencies(self):
        root_process = self._move_to_given_user_and_return_this_process(user="root", logfile=self._open_and_get_logging_file())
        assert self._is_login_succeed(user="root", process=root_process), "\nLogging as root impossible\n"
        # TODO add parsing output of lte-lmts installator - to guarantee dynamical insallation of dependencies
        root_process.sendline('/usr/bin/apt-get -y clean; /usr/bin/apt-get -y update;')
        sys.stderr.write(root_process.before)
        match_index = root_process.expect([".*root@.*"])
        if match_index != 0:
            sys.stderr.write(match_index)
            raise Exception  # TODO add own exceptions
        for package in self.MISSING_PACKAGES:
            root_process.sendline('/usr/bin/apt-get -y install %s' % package)
            match_index = root_process.expect(['root@.*'])
            if match_index == 0:
                sys.stderr.write(root_process.before)
                sys.stderr.write(root_process.after)
            else:
                sys.stderr.write(match_index)  # TODO only for tests
                sys.stderr.write(root_process.before)
                sys.stderr.write(root_process.after)

    def _create_given_folders_tree_if_not_exists(self, complete_path):
        if not os.path.exists(complete_path):
            os.makedirs(complete_path)
        else:
            pass

    def _open_and_get_logging_file(self, path="/home/ute/", filename="lmts_manager_logs.log"):  # maybe logfile in pexpect is better option?
        return open(path+filename, 'a+')

    def _try_to_create_folder_in_remote_system(self, ftp_client, folder_path):
        try:
            ftp_client.mkdir(path=folder_path, mode=0711)
        except IOError as ioerr:
            print(ioerr.args)
            print "\n"*2
            raise Exception

    def _is_existing_folder_in_remote_system(self, complete_path, ftp_client=None):
        """
        :param ftp_client: remote system client
        :return:
        """
        try:
            if ftp_client is not None:
                ftp_client.chdir(complete_path)
            else:
                self.ftp_client.chdir(complete_path)
            return True
        except NameError as nameerr:
            print(nameerr.args)
            return False

    def _get_latest_lmts_deb_pkg_name_available_in_remote_system(self, path_to_folder_with_package):  # TODO changing path.* param to
        return self.ftp_client.listdir(path_to_folder_with_package)[0]


if __name__ == "__main__":
    LmtsManager().download_lmts_package_from_server()
    sys.stderr.write("after download\n")
    LmtsManager().install_lmts_package_via_dpkg("/home/ute/lte-lmts_8.0.1.01-1.06_amd64.deb")
    sys.stderr.write("after install\n")
    LmtsManager().initialize_lmts()
