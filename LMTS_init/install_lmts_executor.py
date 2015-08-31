__author__ = 'tarsa'

import pexpect

#TODO if installed ver is actual we should do not do anything
def _download_lmts_package_from_server(central_server_IP='10.83.200.35', user="ltebox", password='Motorola'):
    pass

def _install_lte_lmts_package(central_server_IP='10.83.200.35'):
    pass

def _update_apt_get():
    updating_apt_get_process = pexpect.run("sudo apt-get update")
    upgrading_apt_get_process = pexpect.run("sudo apt-get upgrade")
    install_apt_get_dependences_process = pexpect.spawn("sudo apt-get -f install")
    match_index = install_apt_get_dependences_process.expect([".*Do you want to continue [Y/n]?.+",
                                             pexpect.TIMEOUT,
                                             pexpect.EOF],
                                            timeout=10)
    if match_index == 0:
        install_apt_get_dependences_process.sendline("Y\n")

    "After this operation, 55.4 MB of additional disk space will be used."
    #Do you want to continue [Y/n]? "

    """
    Starting FTP server: vsftpd.
    [ ok ] Stopping NTP server: ntpd.
    [ ok ] Starting NTP server: ntpd.
    Setting up blt (2.4z-4.2) ...
    Setting up python-tk (2.7.3-1) ...
    Processing triggers for python-support ...



    ute@IAV-KRA-TL166:~$ sudo dpkg -i lte-lmts_8.0.1.01-1.05_amd64.deb
(Reading database ... 134155 files and directories currently installed.)
Preparing to replace lte-lmts 8.0.1.01-1.05 (using lte-lmts_8.0.1.01-1.05_amd64.deb) ...
[ ok ] Shutting down LTE-LMTS Executor:.
[ ok ] Shutting down LTE-LMTS trace:.
Unpacking replacement lte-lmts ...
Setting up lte-lmts (8.0.1.01-1.05) ...

Please edit /usr/lmts/etc/lmts.ini and run 'config update'/
'config remote update' on executor console

Consult /usr/lmts/lib/ini/lmts.ini.template or
/usr/lmts/doc/lmts.ini.html for parameters descriptions



[ ok ] Starting up LMTS Executor:.
[ ok ] Starting up LMTS trace :.
[ ok ] Stopping NTP server: ntpd.
[ ok ] Starting NTP server: ntpd.
ute@IAV-KRA-TL166:~$

    """

    """
    Reading package lists... Done
    Building dependency tree
    Reading state information... Done
    0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.

    """

def _install_lmts_package(path_to_package="", package_name='lte-lmts_8.0.1.01-1.05_amd64.deb'):
    install_lmts_executor = pexpect.run("sudo dpkg -i %s" % package_name)
    print install_lmts_executor

_install_lmts_package()