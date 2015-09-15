__author__ = 'kgadek'


import paramiko
import os


def download_files(hostname='10.83.200.35', username='ltebox', password='Motorola'):
    path_to_files = '/home/ltebox/public_html/apache_files/'
    ivk_file = 'ivk.conf'
    lte_lmts_file = 'lte-lmts.conf'
    path = '/home/ute/'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname, username=username, password=password)
    ftp = ssh.open_sftp()
    ftp.get(os.path.join(path_to_files, ivk_file), os.path.join(path, ivk_file))
    ftp.get(os.path.join(path_to_files, lte_lmts_file), os.path.join(path, lte_lmts_file))
    ftp.close()


if __name__ == "__main__":
    download_files()
