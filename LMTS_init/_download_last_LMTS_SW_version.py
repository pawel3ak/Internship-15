__author__ = 'tarsa'

import paramiko

def _download_LMTS_SW_from_server(hostname='10.83.200.35', username='ltebox', password='Motorola'):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname, username=username, password=password)
    ftp = ssh.open_sftp()
    lmts_package_name = ftp.listdir(path='/home/ltebox/public_html/ute_packages/lmts/')[0]
    ftp.get('/home/ltebox/public_html/ute_packages/lmts/%s' % lmts_package_name, '/home/ute/%s' % lmts_package_name )
    ftp.close()