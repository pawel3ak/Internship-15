import socket
from os import fork


host = "127.0.0.1"
port = 5000
host = (host,port)
data = "zapytani"

sock = socket.socket(family= socket.AF_INET, type= socket.SOCK_DGRAM)
sock.bind(host)
a = fork()
if a == 0:
    while True:
        sock.connect
        sock.sendto(data,host)
        from time import sleep
        sleep(1)
else:
    while True:
        data,addr = sock.recvfrom(1024)
        print "data = {data} \naddr={addr}".format(data=data, addr=addr)

