#!/opt/ute/python/bin/python
# -*- coding: utf-8 -*-
"""
:created on: '21/08/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nokia.com
"""

import socket
import sys
import json
import argparse

HOST_IP, HOST_PORT = "127.0.0.1", 50010


def get_all(sock):
    sock.send("request/get_all")
    while True:
        response = sock.recv(1024)
        if not response == "":
            print response
        elif response == "":
            break
    sock.close()

def get_info(sock, id):
    sock.send("request/get_info")
    while True:
        response = sock.recv(1024)
        try:
            id = int(id)
            if not response == "OK": break
            sock.send(str(id))
            response = sock.recv(1024)
            if response == "": break
            print response
        except:
            break


        # if response == 'OK':
        #     sock.send(str(id))
        #     response = sock.recv(1024)
        #     print response
        # elif response == "":
        #     break
    sock.close()

def get_tlname(sock, cloud):
    sock.send("request/get_testline&cloud={}".format(cloud))
    try:
        response = sock.recv(1024)
        if response != "": print response
    except:
        pass


def set_freetl(sock, freetl):
    sock.send("request/free_testline={}".format(freetl))
    try:
        response = sock.recv(1024)
        if response != "": print response
    except:
        pass


def get_status(sock, status):
    if status == "server":
        sock.send("request/manager_status")
        try:
            response = sock.recv(1024)
            if response != "": print response
        except:
            pass
    else:
        print "request/status_of_={}".format(status)
        sock.send("request/status_of_={}".format(status))
        try:
            response = sock.recv(1024)
            if response != "": print response
        except:
            pass


def get_end_date(sock, TLname):
    sock.send("request/get_end_date_of_={}".format(TLname))
    try:
        response = sock.recv(1024)
        if response != "": print response
    except:
        pass


def delete_from_blacklist(sock, TL_blacklist):
    sock.send("request/blacklist_remove_TL={}".format(TL_blacklist))
    try:
        response = sock.recv(1024)
        if response != "": print response
    except:
        pass

def send_eNB_build_version(sock, build):
    sock.send("eNB_Build={}".format(build))
    try:
        response = sock.recv(1024)
        if response != "": print response
    except:
        pass


def main():
    parser = argparse.ArgumentParser(argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-a', '--host', default=HOST_IP,
                        help='set IP addres for server')
    parser.add_argument('-p', '--port', type=int, default=HOST_PORT,
                        help='set port number for server')
    parser.add_argument('--info', default='',
                        help='check informations about given ID')
    parser.add_argument('--gettl', default='',
                        help='check informations about given ID')
    parser.add_argument('--freetl', default='',
                        help='free tl')
    parser.add_argument('-s', '--status', type=str, default='',
                        help='ask for status')
    parser.add_argument('-d', '--date', type=str, default='',
                        help='ask for end_date')
    parser.add_argument('-r', '--remove', default='',
                        help='remove form blacklist')
    parser.add_argument('--build', type=str, default='None',
                        help='eNB version')


    args = parser.parse_args()
    host = args.host
    port = args.port
    info = args.info
    cloud = args.gettl
    freetl = args.freetl
    status = args.status
    TLname = args.date
    TL_blacklist = args.remove
    build = args.build

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    if info != '':
        if info == 'all':
            get_all(sock)
        else:
            try:
                info = int(info)
                get_info(sock,info)
            except:
                pass

    elif cloud != '':
        get_tlname(sock, cloud)

    elif freetl !='':
        set_freetl(sock, freetl)

    elif status !='':
        get_status(sock, status)

    elif TLname !='':
        get_end_date(sock, TLname)

    elif not TL_blacklist == '':
        delete_from_blacklist(sock, TL_blacklist)

    elif not build == '':
        send_eNB_build_version(sock, build)
    # elif len(sys.argv) == 3:
    #     if sys.argv[1] == "info":
    #         get_info(sock,sys.argv[2])

if __name__ == '__main__':
    main()
