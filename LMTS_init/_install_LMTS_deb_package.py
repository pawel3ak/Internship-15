import pexpect, logging

logger = logging.getLogger("LMTS_install_logger")
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('spam.log')
fh.setLevel(logging.DEBUG)


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

def _install_lmts_package(path_to_package="/home/ute", package_name='lte-lmts_8.0.1.01-1.05_amd64.deb'):
    #TODO name of package is generic
    install_lmts_executor = pexpect.spawn("sudo dpkg -i %s/%s" % (path_to_package ,package_name))
    match_index = install_lmts_executor.expect([".*[ ok ] Starting NTP server: ntpd.", # correct installation case
                                                ".*Errors were encountered while processing:.+", #wrong case
			       	                            pexpect.TIMEOUT,
                              		            pexpect.EOF],
	                                         timeout=10))
    if match_index == 0:



"""
        sudo dpkg -i lte-lmts_8.0.1.01-1.05_amd64.deb
Selecting previously unselected package lte-lmts.
(Reading database ... 131360 files and directories currently installed.)
Unpacking lte-lmts (from lte-lmts_8.0.1.01-1.05_amd64.deb) ...
Creating lmts user account
Creating lmts group
dpkg: dependency problems prevent configuration of lte-lmts:
 lte-lmts depends on libconfig-inifiles-perl; however:
  Package libconfig-inifiles-perl is not installed.
 lte-lmts depends on python-apsw; however:
  Package python-apsw is not installed.
 lte-lmts depends on python-matplotlib; however:
  Package python-matplotlib is not installed.
 lte-lmts depends on python-wxgtk2.8; however:
  Package python-wxgtk2.8 is not installed.
 lte-lmts depends on python-pexpect; however:
  Package python-pexpect is not installed.
 lte-lmts depends on vsftpd; however:
  Package vsftpd is not installed.
 lte-lmts depends on lib32readline5; however:
  Package lib32readline5 is not installed.

dpkg: error processing lte-lmts (--install):
 dependency problems - leaving unconfigured
Errors were encountered while processing:
 lte-lmts

"""

"""
sudo apt-get -f install
Reading package lists... Done
Building dependency tree
Reading state information... Done
Correcting dependencies... Done
The following extra packages will be installed:
  blt fonts-lyx lib32readline5 libconfig-inifiles-perl python-apsw
  python-dateutil python-matplotlib python-matplotlib-data python-pexpect
  python-pyparsing python-tk python-tz python-wxgtk2.8 python-wxversion vsftpd
Suggested packages:
  blt-demo python-apsw-doc dvipng ipython python-configobj python-excelerator
  python-matplotlib-doc python-qt4 python-scipy python-traits
  texlive-extra-utils texlive-latex-extra tix python-tk-dbg wx2.8-doc
  wx2.8-examples editra
The following NEW packages will be installed:
  blt fonts-lyx lib32readline5 libconfig-inifiles-perl python-apsw
  python-dateutil python-matplotlib python-matplotlib-data python-pexpect
  python-pyparsing python-tk python-tz python-wxgtk2.8 python-wxversion vsftpd
0 upgraded, 15 newly installed, 0 to remove and 0 not upgraded.
1 not fully installed or removed.
Need to get 16.2 MB of archives.
After this operation, 55.4 MB of additional disk space will be used.
Do you want to continue [Y/n]? Y
Get:1 http://repo.wroclaw.nsn-rdnet.net/debian/ wheezy/main libconfig-inifiles-perl all 2.75-1 [54.8 kB]
Get:2 http://repo.wroclaw.nsn-rdnet.net/debian/ wheezy/main python-apsw amd64 3.7.6.3-r1-1 [200 kB]
Get:3 http://repo.wroclaw.nsn-rdnet.net/debian/ wheezy/main python-dateutil all 1.5+dfsg-0.1 [55.3 kB]
Get:4 http://repo.wroclaw.nsn-rdnet.net/debian/ wheezy/main fonts-lyx all 2.0.3-3 [167 kB]
Get:5 http://repo.wroclaw.nsn-rdnet.net/debian/ wheezy/main python-matplotlib-data all 1.1.1~rc2-1 [2,057 kB]
Get:6 http://repo.wroclaw.nsn-rdnet.net/debian/ wheezy/main python-pyparsing all 1.5.6+dfsg1-2 [64.7 kB]
Get:7 http://repo.wroclaw.nsn-rdnet.net/debian/ wheezy/main python-tz all 2012c-1 [39.9 kB]
Get:8 http://repo.wroclaw.nsn-rdnet.net/debian/ wheezy/main python-matplotlib amd64 1.1.1~rc2-1 [2,695 kB]
Get:9 http://repo.wroclaw.nsn-rdnet.net/debian/ wheezy/main python-wxversion all 2.8.12.1-12 [91.8 kB]
Get:10 http://repo.wroclaw.nsn-rdnet.net/debian/ wheezy/main python-wxgtk2.8 amd64 2.8.12.1-12 [8,579 kB]
Get:11 http://repo.wroclaw.nsn-rdnet.net/debian/ wheezy/main python-pexpect all 2.4-1 [123 kB]
Get:12 http://repo.wroclaw.nsn-rdnet.net/debian/ wheezy/main vsftpd amd64 2.3.5-3 [158 kB]
Get:13 http://repo.wroclaw.nsn-rdnet.net/debian/ wheezy/main lib32readline5 amd64 5.2+dfsg-2~deb7u1 [143 kB]
Get:14 http://repo.wroclaw.nsn-rdnet.net/debian/ wheezy/main blt amd64 2.4z-4.2 [1,694 kB]
Get:15 http://repo.wroclaw.nsn-rdnet.net/debian/ wheezy/main python-tk amd64 2.7.3-1 [50.9 kB]
Fetched 16.2 MB in 3s (4,207 kB/s)
Preconfiguring packages ...
Selecting previously unselected package libconfig-inifiles-perl.
(Reading database ... 131754 files and directories currently installed.)
Unpacking libconfig-inifiles-perl (from .../libconfig-inifiles-perl_2.75-1_all.deb) ...
Selecting previously unselected package python-apsw.
Unpacking python-apsw (from .../python-apsw_3.7.6.3-r1-1_amd64.deb) ...
Selecting previously unselected package python-dateutil.
Unpacking python-dateutil (from .../python-dateutil_1.5+dfsg-0.1_all.deb) ...
Selecting previously unselected package fonts-lyx.
Unpacking fonts-lyx (from .../fonts-lyx_2.0.3-3_all.deb) ...
Selecting previously unselected package python-matplotlib-data.
Unpacking python-matplotlib-data (from .../python-matplotlib-data_1.1.1~rc2-1_all.deb) ...
Selecting previously unselected package python-pyparsing.
Unpacking python-pyparsing (from .../python-pyparsing_1.5.6+dfsg1-2_all.deb) ...
Selecting previously unselected package python-tz.
Unpacking python-tz (from .../python-tz_2012c-1_all.deb) ...
Selecting previously unselected package python-matplotlib.
Unpacking python-matplotlib (from .../python-matplotlib_1.1.1~rc2-1_amd64.deb) ...
Selecting previously unselected package python-wxversion.
Unpacking python-wxversion (from .../python-wxversion_2.8.12.1-12_all.deb) ...
Selecting previously unselected package python-wxgtk2.8.
Unpacking python-wxgtk2.8 (from .../python-wxgtk2.8_2.8.12.1-12_amd64.deb) ...
Selecting previously unselected package python-pexpect.
Unpacking python-pexpect (from .../python-pexpect_2.4-1_all.deb) ...
Selecting previously unselected package vsftpd.
Unpacking vsftpd (from .../vsftpd_2.3.5-3_amd64.deb) ...
Selecting previously unselected package lib32readline5.
Unpacking lib32readline5 (from .../lib32readline5_5.2+dfsg-2~deb7u1_amd64.deb) ...
Selecting previously unselected package blt.
Unpacking blt (from .../blt_2.4z-4.2_amd64.deb) ...
Selecting previously unselected package python-tk.
Unpacking python-tk (from .../python-tk_2.7.3-1_amd64.deb) ...
Processing triggers for man-db ...
Processing triggers for fontconfig ...
Setting up libconfig-inifiles-perl (2.75-1) ...
Setting up python-apsw (3.7.6.3-r1-1) ...
Setting up python-dateutil (1.5+dfsg-0.1) ...
Setting up fonts-lyx (2.0.3-3) ...
Setting up python-matplotlib-data (1.1.1~rc2-1) ...
Setting up python-pyparsing (1.5.6+dfsg1-2) ...
Setting up python-tz (2012c-1) ...
Setting up python-matplotlib (1.1.1~rc2-1) ...
Setting up python-wxversion (2.8.12.1-12) ...
Setting up python-wxgtk2.8 (2.8.12.1-12) ...
update-alternatives: using /usr/lib/wx/python/wx2.8.pth to provide /usr/lib/wx/python/wx.pth (wx.pth) in auto mode
Setting up python-pexpect (2.4-1) ...
Setting up vsftpd (2.3.5-3) ...
invoke-rc.d: policy-rc.d denied execution of start.
Setting up lib32readline5 (5.2+dfsg-2~deb7u1) ...
Setting up lte-lmts (8.0.1.01-1.05) ...

Please edit /usr/lmts/etc/lmts.ini and run 'config update'/
'config remote update' on executor console

Consult /usr/lmts/lib/ini/lmts.ini.template or
/usr/lmts/doc/lmts.ini.html for parameters descriptions



[ ok ] Starting up LMTS Executor:.
[ ok ] Starting up LMTS trace :.
Enabling site default-ssl.
To activate the new configuration, you need to run:
  service apache2 reload
Enabling module ssl.
See /usr/share/doc/apache2.2-common/README.Debian.gz on how to configure SSL and create self-signed certificates.
To activate the new configuration, you need to run:
  service apache2 restart
[ ok ] Restarting web server: apache2 ... waiting .
Stopping FTP server: No /usr/sbin/vsftpd found running; none killed.
vsftpd.
Starting FTP server: vsftpd.
[ ok ] Stopping NTP server: ntpd.
[ ok ] Starting NTP server: ntpd.
Setting up blt (2.4z-4.2) ...
Setting up python-tk (2.7.3-1) ...
Processing triggers for python-support ...

"""

"""
sudo dpkg -i lte-lmts_8.0.1.01-1.05_amd64.deb
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
"""