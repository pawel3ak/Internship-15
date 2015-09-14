__author__ = 'tarsa'

import re

TGR_IPs = []

def is_tgrs_reachable():
    for IP in TGR_IPs:
        print(pexpect.run("ping {tgr_ip}".format(tgr_ip=)))
        if re.search("", ping_cmd_output)


def parse_TGR_IPs_list_lmts_ini_file(path_to_lmts_ini_file="/usr/lmts/etc/lmts.ini",
                                     first_line = '\[tgr_*',
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
        number_of_lines = sum(1 for line in lmts_configuration)
        lmts_configuration.seek(0)
        for number_of_line in range(0, number_of_lines):
            line=lmts_configuration.readline()
            if re.match(first_line, line):
                line_with_ip_addr = lmts_configuration.readline()
                number_of_line += 1
                _tgr_IP = re.search(second_line, line_with_ip_addr).group(1)
                TGR_IPs.append(_tgr_IP)


def get_list_of_TGR_IPs():
    pass


parse_TGR_IPs_list_lmts_ini_file()
