#!/opt/ute/python/bin/python

import socket
import sys

HOST_IP, HOST_PORT = "127.0.0.1",50000
host = (HOST_IP,HOST_PORT)

try:
    sock = socket.socket(family= socket.AF_INET, type= socket.SOCK_DGRAM)
    if sys.argv > 1:
        data = ""
        for message in sys.argv[1:]:
            pass
            data += str(message) + " "
        sock.sendto(data,host)

    data, addr = sock.recvfrom(1024)
    print "Received information = {data}\nInformation from = {addr}".format(
        data= data, addr= addr)
except:
    print("cos sie nie udalo")
