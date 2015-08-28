__author__ = 'kgadek'

import pexpect
from bs4 import BeautifulSoup
import os


url="http://infrastructure.emea.nsn-net.net/projects/btstools/lte_lmts/"
auth="--password Flexi1234^ --user ivnsn"
new_terminal=pexpect.spawn("/bin/bash")     #we create a new terminal
directory="/home/ute/PycharmProjects/lmts"

def find_name(output):
    start="index.html"
    stop="\'"
    name=output.split(start)[1].split(stop)[0]
    return "index.html"+name

def get_page(url):
    new_terminal.sendline("wget "+url)
    new_terminal.expect("saved",timeout=600)
    output=(  new_terminal.before )
    return output

def get_page_with_auth(url,auth):
    new_terminal.sendline("wget "+url+" "+auth)
    new_terminal.expect("saved",timeout=600)
    output=(  new_terminal.before )
    return output

def find_text(name_of_file,find,tag):
    file=open(name_of_file,"r")
    soup=BeautifulSoup(file,"html.parser")
    wynik=[]
    for node in soup.findAll(tag):
        string=''.join(node.findAll(text=True))
        if find in string:
            wynik.append(string)
    return wynik


def check_rel():

    output=get_page(url)
    name_of_file=find_name(output)
    print (  "We find number of new upgrade" )

    #find name of curren rel
    R_list=find_text(name_of_file," LMTS latest build",'a')
    R_number= R_list[0].replace(" LMTS latest build","")
    ##parse secound url
    url2="http://lte.americas.nsn-net.net/scm/enb_official_builds/"+R_number+".0/LTE-LMTS/"
    #print url2
    output2=get_page_with_auth(url2,auth)
    #name_of_file=find_name(output)

    name_of_file2=find_name(output2)
    names_of_rel=find_text(name_of_file2,"LTE-LMTS_",'li')
    how_many_rel=len(names_of_rel)
    name_of_a_folder=names_of_rel[how_many_rel-1].replace(" ","")


    #download a file

    print "Download a file..."
    name_of_a_file_to_download=name_of_a_folder.lower().replace("/","")
    name_of_a_file_to_download=name_of_a_file_to_download.replace("r","")
    name_of_a_file_to_download=name_of_a_file_to_download.replace("_bld-1.01",".1.01-1")
    print "Name of a new rel: "+name_of_a_file_to_download
    check_version=""
    for file in os.listdir(directory):
        if file==name_of_a_file_to_download+"_amd64.deb":
            check_version= "We have this"
            break
    if not check_version:
        url_download=url2+name_of_a_folder+name_of_a_file_to_download
        #print "wget "+url_download+"_amd64.deb"+" "+auth
        new_terminal.sendline("wget "+url_download+"_amd64.deb"+" "+auth)
        new_terminal.expect("saved",timeout=1200)
        print new_terminal.before
    print "Done"
    new_terminal.sendline("rm "+name_of_file)
    new_terminal.sendline("rm "+name_of_file2)
    new_terminal.sendline("exit")

if __name__ == "__main__":
    check_rel()
