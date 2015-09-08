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

def get_tlname(sock):
    sock.send("request/get_testline")
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

def main():
    parser = argparse.ArgumentParser(argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-a', '--host', default=HOST_IP,
                        help='set IP addres for server')
    parser.add_argument('-p', '--port', type=int, default=HOST_PORT,
                        help='set port number for server')
    parser.add_argument('--info', default='',
                        help='check informations about given ID')
    parser.add_argument('--tl', default='',
                        help='check informations about given ID')
    parser.add_argument('--freetl', default='',
                        help='not yet')
    args = parser.parse_args()
    host = args.host
    port = args.port
    info = args.info
    tl = args.tl
    freetl = args.freetl

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
    elif tl != '':
        get_tlname(sock)
    elif freetl !='':
        set_freetl(sock, freetl)
    # elif len(sys.argv) == 3:
    #     if sys.argv[1] == "info":
    #         get_info(sock,sys.argv[2])

if __name__ == '__main__':
    main()
