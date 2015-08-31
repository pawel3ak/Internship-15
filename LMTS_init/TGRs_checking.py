__author__ = 'tarsa'

import re

TGR_IPs = []

def is_tgrs_reachable():
    for IP in TGR_IPs:
        print(pexpect.run("ping {tgr_ip}".format(tgr_ip=)))
        if re.search("", ping_cmd_output)


def parse_TGR_IPs_list_lmts_ini_file(path_to_lmts_ini_file="/usr/lmts/etc/lmts.ini",
                                     first_line = "[tgr_\d]",
                                     second_line = "ip_addr.+= (\d+\.\d+\.\d+.\d+)"):
    """
    [tgr_1]
    ip_addr                     = 10.60.0.4                              < -- 1st interesting IP
    ss_ip_addr_pool             = 185.4.0.0/16
    ss_interface                = eth0
    side                        = SS
    password                    = emssim
    [tgr_2]
    ip_addr                     = 10.60.0.3                              < -- 2nd interesting IP  #can be more than 2? is there always 2? Do this sections have same composition?
    ue_interface                = eth0
    side                        = MS
    password                    = emssim

    :return:
    """

    current_line = None
    previous_line = None

    with open(path_to_lmts_ini_file, 'r') as lmts_configuration:
        previous_line = lmts_configuration.readline()
	print "First line: " + previous_line + "\n"
        for line in lmts_configuration:
            current_line = line
            if re.match(first_line, previous_line):
                _tgr_IP = re.search(second_line, current_line).group(0)
                TGR_IPs.append(_tgr_IP)
	    previous_line = current_line


def get_list_of_TGR_IPs():
    pass


parse_TGR_IPs_list_lmts_ini_file()
