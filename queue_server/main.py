import socket
import subprocess
import multiprocessing as mp
import select
import argparse

#default variables
HOST_IP, HOST_PORT = "127.0.0.1",50000
EOL = u'\n\r\n'

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-a', '--host', default=HOST_IP,
                        help='set IP addres for server')
    parser.add_argument('-p', '--port', type=int, default=HOST_PORT,
                        help='set port number for server')

    # override defaults if got
    args = parser.parse_args()
    host = args.host
    port = args.port

    try:
        serversocket = socket.socket(family= socket.AF_INET, type= socket.SOCK_DGRAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        serversocket.bind((host, port))


        while True:
            data,addr = serversocket.recvfrom(1024)
            print "data = {data} \naddr={addr}".format(data=data, addr=addr)
            serversocket.sendto(data,addr)


    except:
        print "what?"
        pass



if __name__ == '__main__':
    main()
