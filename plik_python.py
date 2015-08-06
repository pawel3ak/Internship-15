__author__ = 'kgadek'
import urllib2
from bs4 import BeautifulSoup
proxy_handler = urllib2.ProxyHandler({'http': '87.254.212.120:8080',
                                     'https': '87.254.212.120:8080'})
url="http://www.gmail.com"
login="klaudia.g.1993@gmail.com"
password="zielony4327"
password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
password_mgr.add_password(None, url ,login ,password )
password_handler = urllib2.HTTPBasicAuthHandler(password_mgr)
opener = urllib2.build_opener(proxy_handler,password_handler)
urllib2.install_opener(opener)
response = urllib2.urlopen(url)
soup=BeautifulSoup(response,"html.parser")
for id in soup.find_all("a"): #wpisac tag przed id
    id_version=id.get('href')
    print id_version
response.close()
