__author__ = 'ute'
import urllib2
import time
from bs4 import BeautifulSoup
current_version=6601
while(True):
    current_version+=1
    try:
        url='http://pddb.inside.nokiasiemensnetworks.com/pddb/reports/Report.do?relid='+str(current_version)+'&basereleaseincluded=yes&hiddenincluded=no&deletedincluded=no'
        response = urllib2.urlopen(url)
        soup=BeautifulSoup(response,"html.parser")
        print "Jest link, ale czy jest produkt?"
        product=0
        for id in soup.find_all("header"):
            if ((str(id.get("id"))==str(current_version)) and (str(id.get("product"))=="LTE BTS")):
                print current_version
                print id.get("release")
                print "tak"
                ###uruchamiam skrypt perlowy
                product=1
                break
        if product==0:
            print "nie"
        response.close()
    except urllib2.URLError:
        print "Nie ma linku"
        print current_version
        current_version-=1
    time.sleep(3600)
    print "\n"
