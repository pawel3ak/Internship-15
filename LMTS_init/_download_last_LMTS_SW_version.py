__author__ = 'tarsa'

import paramiko


def check_path(path, ftp):
    try:
        ftp.chdir(path)
    except:
        ftp.mkdir(path)


def get_lmts_package_name(built_version, ftp, path):
    if built_version and built_version in ftp.listdir(path):
        lmts_package_name = built_version
    elif built_version:
        for file_name in ftp.listdir(path):
            if file_name.find(built_version + "_amd64.deb"):
                lmts_package_name = file_name
                break
    else:
        lmts_package_name = ftp.listdir(path='/home/ltebox/public_html/ute_packages/lmts/')[0]
    return lmts_package_name


def _download_LMTS_SW_from_server(hostname='10.83.200.35', username='ltebox', password='Motorola', built_version=False):
    path = '/home/ltebox/public_html/ute_packages/lmts/'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname, username=username, password=password)
    ftp = ssh.open_sftp()
    check_path(path, ftp)
    lmts_package_name = get_lmts_package_name(built_version, ftp, path)
    ftp.get(path + lmts_package_name, '/home/ute/lmts_software/%s' % lmts_package_name)
    ftp.close()

_download_LMTS_SW_from_server(built_version="06")
