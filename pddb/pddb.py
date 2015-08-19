__author__ = 'kgadek'
import urllib2
import time
import pexpect
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import logging
import logging.handlers
import sys


def send_message(current_version,name_of_version):
    server=smtplib.SMTP('10.150.129.55')
    server.ehlo()
    server.starttls()
    server.ehlo()
    #server.login(login, pass) jestem juz zalogowana wiec nie ma sensu
    sender='klaudia.gadek@nokia.com'#
    wiadomosc=("\nThere is a new version o PDDB available!\n\nId_version: "+str(current_version)+"\nName of version: "+str(name_of_version))
    m = MIMEText(wiadomosc)
    m['Subject'] = 'New PDDB version'
    m['From'] = 'pddb.downloader@nokia.com'
    mails=open('mail_list.txt')
    for receiver in mails.readlines():
        m['To'] = receiver
        server.sendmail(sender, receiver, m.as_string())#from,to,message
    server.close()
    logger.info(  "We send all messages" )

def download_version(current_version):
    new_terminal=pexpect.spawn("/bin/bash")
    new_terminal.sendline("cd /home/ltebox/public_html/sstlib_scripts/LTE/FA_OM/tools/EMSS/scripts")
    new_terminal.sendline("perl GetPDDB.pl "+str(current_version))
    new_terminal.expect("Finish",timeout=600)
    logger.info(  new_terminal.before )
    logger.info(  "Done" )
    new_terminal.sendline("exit")

current_version=6602

#Create a logger
LOG_FILENAME = 'PDDB_downloader_logs.log'
logger=logging.getLogger('Logger')
logger.setLevel(logging.DEBUG)
format = logging.Formatter("%(asctime)s - %(name)s- %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
logger.addHandler(ch)
fh = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=(1048576*5), backupCount=0)
fh.setFormatter(format)
logger.addHandler(fh)
logger.info("Log database\n")

#Proxy
proxy_handler = urllib2.ProxyHandler({})#chyba
opener = urllib2.build_opener(proxy_handler)
urllib2.install_opener(opener)

while(True):
    logger.info(  "Check a new PDDB version")
    current_version+=1
    try:
        url='http://pddb.inside.nokiasiemensnetworks.com/pddb/reports/Report.do?relid='+str(current_version)+'&basereleaseincluded=yes&hiddenincluded=no&deletedincluded=no'
        response = urllib2.urlopen(url)
        logger.info( "There is a link, let's parse")
        soup=BeautifulSoup(response,"html.parser")
        logger.info(  "Parser is running...")
        product=0
        for id in soup.find_all("header"):
            if ((str(id.get("id"))==str(current_version)) and (str(id.get("product"))=="LTE BTS")):
                    if (any(soup.findAll(attrs={"class" : "AMGR"})) or any(soup.findAll(attrs={"class" : "ADIPNO"}))):
                        logger.info(  current_version)
                        name_of_version=id.get("release")
                        logger.info(  name_of_version )
                        logger.info(  "New release")
                        download_version(current_version)
                        send_message(current_version,name_of_version)
                        product=1
                        break
                        break
        if product==0:
            logger.info(  "Not for our product")
            logger.info(  current_version)
        response.close()
    except urllib2.URLError:
        logger.info(  "We wait for a new release")
        logger.info(  current_version)
        current_version-=1
        time.sleep(3600)
    logger.info(  "\n")
