import pexpect

def _install_lmts_package(path_to_package="", package_name='lte-lmts_8.0.1.01-1.05_amd64.deb'):
    install_lmts_executor = pexpect.run("sudo dpkg -i %s" % package_name)
    print install_lmts_executor


