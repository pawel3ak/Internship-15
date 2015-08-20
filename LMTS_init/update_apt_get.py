__author__ = 'tarsa'

import pexpect

#TODO add logging

def _update_apt_get():
    updating_apt_get_process = pexpect.run("sudo apt-get update")
    upgrading_apt_get_process = pexpect.spawn("sudo apt-get -f upgrade")
    match_index = upgrading_apt_get_process.expect([".*Do you want to continue [Y/n]?.+",
			       	                   pexpect.TIMEOUT,
                              		           pexpect.EOF],
	                                          timeout=10)])
    if match_index == 0:
	install_apt_get_dependences_process.sendline("Y\n")

    install_apt_get_dependences_process = pexpect.spawn("sudo apt-get -f install")
    match_index = install_apt_get_dependences_process.expect([".*Do you want to continue [Y/n]?.+",
                                             pexpect.TIMEOUT,
                                             pexpect.EOF],
                                            timeout=10)
    if match_index == 0:
        install_apt_get_dependences_process.sendline("Y\n")

