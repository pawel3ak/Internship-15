
import sys

import json
import re
import urllib2
import base64

import signal
import time
import threading
import local_tests2
from multiprocessing import Manager
import os

class TimerClass(threading.Thread):
    def __init__(self, target, args):
        threading.Thread.__init__(self,target=target, args=args)
        self.event = threading.Event()


    def run(self):
        while not self.event.is_set():
            print "something"
            self.event.wait(10)


_ready = threading.Event()
man = Manager()
dict = man.dict()
dict = {}
threads = []
def signal_SIGINT_handler(_signo, frame):   #nowa obsluga SIGINT
    try:
        print "We have signal SIGINT"
        global threads
        global _ready

        while True:
            i=0
            for thread in threads:
                if thread.isAlive():
                    _ready.set()
                    os.kill(dict[threads.index(thread)], signal.SIGKILL)
                    time.sleep(3)
                    # os.kill(dict[threads.index(thread)], signal.SIGINT)
                else:
                    i+=1
            if i==4: break

    except:
        pass
    finally:
        signal.signal(signal.SIGINT, signal.default_int_handler)    #wracamy do domyslnego dzialania ==
                                                                    #przy powtornym wyslaniu ctrl+c
                                                                    #  zakonczymy program
def signal_SIGTERM_handler(_signo, frame):
    try:
        print "We have signal SIGTERM"
    except:
        pass
    finally:
        signal.signal(signal.SIGTERM, signal.SIG_DFL)

def main():
    signal.signal(signal.SIGINT, signal_SIGINT_handler)         # zmieniamy obsluge SIGINT na nasza funkcje
    signal.signal(signal.SIGTERM, signal_SIGTERM_handler)
    # _ready = threading.Event()
    # thread = TimerClass(target=local_tests2.main, args=[_ready])

    for i in range(0,4):
        thread = threading.Thread(target=local_tests2.main, args=[i, _ready, dict])
        threads.append(thread)
        thread.start()

        # thread.daemon = True

    i=0
    while True:
        print "iterator = ", i
        i+=1
        time.sleep(3)




if __name__ == '__main__':
    main()








#

# a = "Everything up to date."
#
# try:
#     if re.match(".*.(up to date.)", a).groups()[0] != None:
#         print "ok"
#         pass
# except:
#     pass
#     # print "tak"
#
#
# str2="""
# remote: Counting objects: 3, done.
# remote: Compressing objects: 100% (2/2), done.
# remote: Total 3 (delta 1), reused 3 (delta 1), pack-reused 0
# Unpacking objects: 100% (3/3), done.
# From https://github.com/pawel3ak/Internship-15
#    3882d49..26ccbd1  master     -> origin/master
# Updating 3882d49..26ccbd1
# Fast-forward
#  install_test_environment_site_package.log |  228 +++++++++++++++++++++++++++++
#  1 file changed, 228 insertions(+)
#  create mode 100644 install_test_environment_site_package.log
# """
# #
# str="""
# Counting objects: 9, done.
# Compressing objects: 100% (5/5), done.
# Writing objects: 100% (5/5), 476 bytes, done.
# Total 5 (delta 3), reused 0 (delta 0)
# To https://paul105@github.com/pawel3ak/Internship-15.git
#    8a8ea37..3882d49  master -> master
#
# """
# aaa = "git push cos"
# if re.findall("push", aaa):
#     print "t"
#
# while True:
#     if not re.findall("Unpacking objects:.*done", str2) == []:
#         print "ok"
#         break
#
#     else:
#         if not re.findall(".*.up-to-date", str2) == []:
#             print "ok2"
#             break
#
#
#






#
# # uname = base64.encodestring('nogiec')
# # passwd = base64.encodestring('!salezjanierlz3!')
# job_api = jenkins.Jenkins('http://plkraaa-jenkins.emea.nsn-net.net:8080',username='nogiec', password='!salezjanierlz3!')
# # job_api = jenkins.Jenkins('http://plkraaa-jenkins.emea.nsn-net.net:8080', uname, passwd)
# # node = job_api.get_node('tl99_test')
#
# # print job_api.get_version()
# # node = job_api.get_node_config('tl99_test')
# node = job_api.get_node('tl63_test')
# print node
# print node.is_online()
# print node.set_online()
#

# def urlopen(url,username=None, password=None, data=None):
#     '''Open a URL using the urllib2 opener.'''
#     request = urllib2.Request(url, data)
#     base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
#     request.add_header("Authorization", "Basic %s" % base64string)
#     response = urllib2.urlopen(request)
#     return response
#
# result = urlopen('https://qaa.server.com/jenkins', "username", "password")


'''
file_name = ['LTE2465_A_c.LTE2465_A_c_AC_1_S1_Setup_for_CSG_eNB', 'LTE2465_A_d.LTE2465_A_d_AC_1_Inclusion_of_CSG_Id_in_X2AP_mess', 'LTE2465_A_d.LTE2465_A_d_AC_2_Exclusion_of_CSG_Id_in_X2AP_mess', 'LTE2465_A_f.LTE2465_A_f_AC_1_intra_eNB_reestablishment_from_n', 'LTE2465_A_f.LTE2465_A_f_AC_2_intra_eNB_reestablishment_betwee', 'LTE2465_A_f.LTE2465_A_f_AC_3_intra_eNB_reestablishment_betwee', 'LTE2465_A_f.LTE2465_A_f_AC_4_intra_eNB_reestablishment_from_C', 'LTE2465_A_g.LTE2465_A_g_AC_1_inter_eNB_reestablishment_from_n', 'LTE2465_A_g.LTE2465_A_g_AC_3_inter_eNB_reestablishment_from_C']
# GMT_hour = time.gmtime().tm_hour
# local_hour = time.localtime().tm_hour
# print time.localtime().tm_hour -time.gmtime().tm_hour
test = 'LTE2465'
additional_directory = []
file_names = []
for f in file_name:
    try:
        more_informations = re.search('({test}.*)\.({test1}.*)'.format(test=test,test1=test),f).groups()
        additional_directory.append(more_informations[0])
        file_names.append(more_informations[1])
    except:
        pass
# print additional_directory
# print file_names


directory = 'LTE2465'
client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.WarningPolicy)
client.connect('wmp-tl99.lab0.krk-lab.nsn-rdnet.net', username='ute', password='ute')
sftp = client.open_sftp()
if len(additional_directory) != 0:
    for f in range(0,len(file_names)):
        path = '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/{}/tests/{}'.format(directory,additional_directory[f])
        if True:
            files = sftp.listdir(path=path)
            found = False
            for file in files:
                # print file
                try:
                    _file_name = re.search('({name}.*)'.format(name=file_names[f]),file).groups()[0]
                    found = True
                    print _file_name
                    break
                except:
                    pass
            if not found:
                failureStatus = 4
        # except:
        #     pass








'''
"""
Started by user Pawel Nogiec
[EnvInject] - Loading node environment variables.
Building remotely on tl99_test in workspace /home/ute/workspace/test_on_tl99_test
[test_on_tl99_test] $ /bin/sh -xe /tmp/hudson6019102604162988863.sh
+ . /home/ute/virtualenvs/ute/bin/activate
+ deactivate nondestructive
+ unset pydoc
+ [ -n  ]
+ [ -n  ]
+ [ -n  -o -n  ]
+ [ -n  ]
+ unset VIRTUAL_ENV
+ [ ! nondestructive = nondestructive ]
+ VIRTUAL_ENV=/home/ute/virtualenvs/ute
+ export VIRTUAL_ENV
+ _OLD_VIRTUAL_PATH=/opt/ute/python/bin:/usr/local/bin:/usr/bin:/bin:/usr/bin/X11:/usr/games:/opt/ute/jython/bin
+ PATH=/home/ute/virtualenvs/ute/bin:/opt/ute/python/bin:/usr/local/bin:/usr/bin:/bin:/usr/bin/X11:/usr/games:/opt/ute/jython/bin
+ export PATH
+ [ -n  ]
+ [ -z  ]
+ _OLD_VIRTUAL_PS1=$
+ [ x != x ]
+ basename /home/ute/virtualenvs/ute
+ [ ute = __ ]
+ basename /home/ute/virtualenvs/ute
+ PS1=(ute)$
+ export PS1
+ alias pydoc=python -m pydoc
+ [ -n  -o -n  ]
+ python /home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/CRT/ivk_pybot.py -S /home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTEXYZ -c /home/ute/moj_config.yaml -L DEBUG -d /home/ute/logs/tl99_test_2015-08-26_11-16-31
[ ERROR ] Suite 'LTEXYZ' contains no tests with tags 'Release FL16' or 'enable'.
[ ERROR ] jakis inny dziwny blad.
Try --help for usage information.
 - 11:16:33 26/08/2015 -
 - 11:16:33 26/08/2015 -
Elapsed time: 00:00:00.0
+ sshpass -p Motorola scp -r /home/ute/logs/tl99_test_2015-08-26_11-16-31 ltebox@10.83.200.35:public_html/logs/
/home/ute/logs/tl99_test_2015-08-26_11-16-31: No such file or directory
Build step 'Execute shell' marked build as failure
Notifying upstream projects of job completion
Finished: FAILURE


# print output
start = output.find('[ ERROR ]')
# if not start == -1:
#     print output[start:output.find(r'\\\n')]
output = output.split('\n')
iterator=0
for line in output:
    if re.findall('\[.ERROR.\].*no tests.*', line):
        iterator +=1
print iterator



def write_dictionary_to_file(file_name, dictionary):
    with open(file_name, "wb") as open_file:
        json.dump(dictionary, open_file)



print write_dictionary_to_file("ala_ma",{})


dict = {
    'cos': 'tam',
    'inne' : 'cos'
}

b = dict.copy()

b['cos'] = 'aaaa'

print "dict = ", dict
print "b = ", b



print time.altzone/3600


dict = {
    'cos': 'tam',
    'inne' : 'cos'
}

if not 'cos' in dict:
    print "ala"
else:
    print "ma kota"


job_api = jenkinsapi.api.Jenkins('http://plkraaa-jenkins.emea.nsn-net.net:8080')
job_name = 'test_on_tl99_test'
job = job_api.get_job(job_name)
bn = job.get_last_buildnumber()
url = 'http://plkraaa-jenkins.emea.nsn-net.net:8080'
print '{url}/job/{job_name}/{bn}/console'.format(url=url,job_name=job_name,bn=bn)


client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.WarningPolicy)
client.connect('wmp-tl99.lab0.krk-lab.nsn-rdnet.net', username='ute', password='ute')
sftp = client.open_sftp()

path = '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/{}/tests/'.format(directory)


job_api = jenkinsapi.api.Jenkins('http://plkraaa-jenkins.emea.nsn-net.net:8080')
job = job_api.get_job('test_on_tl99_test')
t = job.get_last_build().get_timestamp()
# timestamp.hour -= (time.altzone/3600)

build_time = '{}-{:02g}-{:02g}_{:02g}-{:02g}-{:02g}'.format(t.year, t.month, t.day, (t.hour-(time.altzone/3600)), t.minute, t.second)
tl_name = 'tl99_test'
log_link = 'http://10.83.200.35/~ltebox/logs/{}_{}/log.html'.format(tl_name,build_time)
print log_link
print job.get_last_build().get_result_url()

"""








