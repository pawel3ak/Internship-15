__author__ = 'kgadek'
import urllib2
import time
import pexpect
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup


def send_message(current_version,name):
    server=smtplib.SMTP('10.150.129.55')
    server.ehlo()
    server.starttls()
    server.ehlo()
    #server.login(login, pass) jestem juz zalogowana wiec nie ma sensu
    sender='klaudia.gadek@nokia.com'#
    wiadomosc=("\nThere is a new version o PDDB available!\n\nId_version: "+str(current_version)+"\nName of version: "+str(name))
    m = MIMEText(wiadomosc)
    m['Subject'] = 'New PDDB version'
    m['From'] = sender
    mails=open('mail_list.txt')
    for receiver in mails.readlines():
        m['To'] = receiver
        server.sendmail(sender, receiver, m.as_string())#from,to,message
    server.close()
    print "We send all messages"

def download_version(current_version):
    new_terminal=pexpect.spawn("/bin/bash")
    new_terminal.sendline("sudo perl /home/ute/nowy/Internship15/GetPDDB.pl "+str(current_version))
    new_terminal.expect("Parse duration",timeout=60)
    print new_terminal.before
    print "Done"
    new_terminal.sendline("exit")

current_version=6601
while(True):
    current_version+=1
    try:
        url='http://pddb.inside.nokiasiemensnetworks.com/pddb/reports/Report.do?relid='+str(current_version)+'&basereleaseincluded=yes&hiddenincluded=no&deletedincluded=no'
        response = urllib2.urlopen(url)
        soup=BeautifulSoup(response,"html.parser")
        print "There is a link"
        product=0
        for id in soup.find_all("header"):
            if ((str(id.get("id"))==str(current_version)) and (str(id.get("product"))=="LTE BTS")):
                print current_version
                name=id.get("release")
                print name
                print "New release"
                download_version(current_version)
                send_message(current_version,name)
                product=1
                break
        if product==0:
            print "Not for our product"
            print current_version
        response.close()
    except urllib2.URLError:
        print "No link"
        print current_version
        current_version-=1
        time.sleep(3)
    print "\n"
