__author__ = 'ute'
from multiprocessing import Manager
from threading import Thread
from supervisor import main
from time import sleep


man = Manager()
parent_dict = man.dict()
parent_dict = {}
thread = Thread(target=main, args=["cos","cos",parent_dict,"cos","cos"])
thread.daemon = True
thread.start()
sleep(2)
parent_dict['jeden'] = 'dwa'
sleep(7)
print "rodzic widzi = ", parent_dict

