__author__ = 'ute'
import urllib2
import requests
import time
from bs4 import BeautifulSoup
"""proxy_handler = urllib2.ProxyHandler({'http': '87.254.212.120:8080',
                                     'https': '87.254.212.120:8080'})
"""
url_logowanie=url="http://pddb.inside.nsn.com/pddb"
url="http://pddb.inside.nsn.com/pddb/releases/viewReleases.do?productID=46"#zamienic na pddb.inside.nsn.com
login="kgadek"#co z danymi ? w sumie to mozna miec tylko 1 dane
password="Nokia4327"
password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
password_mgr.add_password(None, url ,login ,password )
password_handler = urllib2.HTTPBasicAuthHandler(password_mgr)
opener = urllib2.build_opener(password_handler)
current_version=6503
urllib2.install_opener(opener)
#response1 = urllib2.urlopen(url_logowanie)
resp=requests.get("http://pddb.inside.nsn.com/pddb/login.jsp", auth=(login, password))
resp=requests.get("http://pddb.inside.nsn.com/pddb", auth=(login, password))
#print resp.content
cookies=resp.cookies
#response = urllib2.urlopen(url)
response = requests.get(url, cookies)
print response.content
"""soup=BeautifulSoup(response,"html.parser")
#print soup
for id in soup.find_all("input"):
        if (str(id.get("name"))=="releaseId"):
            id_version=int(id.get("value"))
            if id_version!=None and int(id_version)>current_version:
                current_version=id_version
                print current_version
response.close()
"""
