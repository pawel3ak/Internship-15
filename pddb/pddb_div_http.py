__author__ = 'ute'
import time
import html2text
from bs4 import BeautifulSoup
html = open("C:\Users\kgadek\PycharmProjects\untitled\Parameter Dictionary.html").read()
soup=BeautifulSoup(html,"html.parser")
current_version=6503
while(True):
    for id in soup.find_all("div"):
        id_version=id.get("releaseid")
        if (id_version!=None and int(id_version)>current_version):
            current_version=id_version
            print current_version#z nazwa bedzie problem
            print id.text
        break
        elif (id_version!=None and int(id_version)==current_version):
        break
    time.sleep(3600)
