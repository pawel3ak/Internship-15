#!/tools/bin/python
# -*- coding: utf-8 -*-
"""
module docstring...
"""
import socket
import select
import argparse
from time import sleep
from threading import Thread
from traceback import format_exc
from multiprocessing import Manager, Process

from utils.jen import jen_checker
from utils.svn import svn_checker
from utils.svr import svr_request, svr_disconnect


# main (default) config
HOST, PORT = '0.0.0.0', 50000
VERSION = '2015/06/30'
EOL = u'\n\r\n'


def queuing(queue, responses, debug):
    """ docstring... """
    from utils.xlm import DictToXml

    if debug: # debug ONLY
        try:
            if isinstance(queue[0], tuple) and len(queue[0]) == 2:
                if isinstance(queue[0][1], str):
                    tmp = str(queue[0][1])
                else:
                    tmp = str(DictToXml(queue[0][1]))

                responses[queue[0][0]] += tmp + EOL
            else:
                print queue[0]

        except Exception, exc:
            print format_exc(exc)

        finally:
            queue.pop(0)

    else: # NON-debug
        try:
            tmp = str(DictToXml(queue[0][1]))
            responses[queue[0][0]] += tmp + EOL

        except:
            pass

        finally:
            queue.pop(0)

def main():
    """ doc string... """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-a', '--host', default=HOST,
                        help='set IP addres for server')
    parser.add_argument('-p', '--port', type=int, default=PORT,
                        help='set port number for server')
    parser.add_argument('--debug', action='store_true',
                        help='run in debug mode')
    parser.add_argument('--ignore-users-filter', action='store_true',
                        help='ignore users\' lists of users')
    parser.add_argument('--version', action='version',
                        version=('%(prog)s ' + VERSION))

    # override defaults if got
    args = parser.parse_args()
    host = args.host
    port = args.port
    debug = args.debug

    try:
        # set up server
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        serversocket.bind((host, port))
        serversocket.listen(1)
        serversocket.setblocking(0)

        # prepare epoll
        epoll = select.epoll()
        epoll.register(serversocket.fileno(), select.EPOLLIN)

        # init dicts for server
        connections = {}
        responses = {}
        requests = {}

        # init global (multiprocess) vars
        man = Manager()
        jobs = man.dict()
        users = man.dict()
        repos = man.dict()
        jenks = man.dict()
        queue = man.list()

        # prepare and run subprocesses
        svn = Process(target=svn_checker,
                      args=(repos, users, jenks, jobs, queue, args))
        jen = Process(target=jen_checker,
                      args=(jobs, users, queue, args))

        svn.start()
        jen.start()

        # let's start
        print "JenkinsNotify/server, version: %s, (%s, %d)%s%s" % (
            VERSION, host, port, ' DEBUG' if debug else '',
            ' IGNORING' if args.ignore_users_filter else '')

        # main server loop
        while True:
            for fileno, event in epoll.poll(1):
                try:
                    if fileno == serversocket.fileno():

                        # new client's connection
                        connection, address = serversocket.accept()
                        connection.setblocking(0)

                        epoll.register(connection.fileno(), select.EPOLLIN)

                        connections[connection.fileno()] = connection
                        responses[connection.fileno()] = u''
                        requests[connection.fileno()] = u''

                        if debug: # debug ONLY
                            queue.append('++users %s' % str(address))

                    elif event & select.EPOLLIN:

                        # get data from clients
                        try:
                            data = connections[fileno].recv(1024)
                        except socket.error:
                            data = None

                        if data:
                            requests[fileno] += data

                            if EOL in requests[fileno]:
                                request = requests[fileno].decode(
                                    )[ : requests[fileno].find(EOL)].strip()

                                # handle the client's request
                                thread = Thread(
                                    target=svr_request,
                                    args=(connections[fileno].getpeername(),
                                          fileno, request, queue, users, repos,
                                          jenks, jobs, args))
                                thread.daemon = True
                                thread.start()

                                epoll.modify(
                                    fileno, select.EPOLLOUT | select.EPOLLIN)
                                requests[fileno] = requests[fileno].decode(
                                    )[requests[fileno].find(EOL)+len(EOL) : ]
                        else:
                            try:
                                epoll.modify(fileno, 0)
                                connections[fileno].shutdown(socket.SHUT_RDWR)
                            except socket.error:
                                pass

                    elif event & select.EPOLLOUT:

                        # send data to clients
                        try:
                            byteswritten = \
                                connections[fileno].send(responses[fileno])
                            responses[fileno] = responses[fileno][byteswritten:]
                        except socket.error:
                            responses[fileno] = u''

                    elif event & select.EPOLLHUP:

                        # close client's connection
                        epoll.unregister(fileno)
                        connections[fileno].close()
                        del connections[fileno]

                        # clear global arrays
                        thread = Thread(
                            target=svr_disconnect,
                            args=(fileno, queue, users, repos, jobs, args))
                        thread.daemon = True
                        thread.start()

                        if debug: # debug ONLY
                            queue.append('--users')

                except Exception, exc:
                    queue.append(format_exc(exc))

            while queue:
                queuing(queue, responses, debug)

            # take a rest
            sleep(0.01)

    finally:
        try:
            # close epoll
            epoll.unregister(serversocket.fileno())
            epoll.close()
        except Exception, exc:
            if debug:
                print format_exc(exc)


if __name__ == '__main__':
    main()
