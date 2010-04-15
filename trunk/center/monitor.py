# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Apr 12, 2010 2:39:16 PM$"

import os, time
import threading

import nodeinfo
from center_global import get_global, set_global

ISOTIMEFMT='%Y-%m-%d %X'

class DaemonHeartBeat(threading.Thread):
    """
    heart beat monitor for all agents to check if daemon is online
    default period time of checking is 30 seconds
    """
    def __init__(self, nodelist, interval=30):
        threading.Thread.__init__(self)
        self.nodelist = nodelist
        self.interval = interval

    def run(self):
        self.stopevent = threading.Event()
        while not self.stopevent.isSet():
            for name, vm in self.nodelist.items():
                try:
                    vm.service.heart_beat()
                except:
                    print '[%s] Daemon %s(%s) is lost' % (time.strftime(ISOTIMEFMT), name, vm.ip)
        return 0

    def join(self, timeout = None):
        self.stopevent.set()
        threading.Thread.join(self, timeout)

class Daemon_Monitor(threading.Thread):
    def __init__(self, node, interval=1):
        threading.Thread.__init__(self)
        self.node = node
        self.interval = interval
#        self.stopevent = threading.Event()

    def run(self):
        self.stopevent = threading.Event()
        ret = self.node.update_perf_info()
        if ret == -2:
            print '[%s] %s is missing' % (time.strftime(ISOTIMEFMT), self.node.name)
            return ret
        elif ret == -1:
            print '[%s] %s is migrated' % (time.strftime(ISOTIMEFMT), self.node.name)
            return ret
        print '[%s] Monitor thread of %s started' % (time.strftime(ISOTIMEFMT), self.node.ip)
        while not self.stopevent.isSet( ):

            ret = self.node.update_perf_info()
            #exceptions
            if ret == -2:
                print '[%s] %s is missing' % (time.strftime(ISOTIMEFMT), self.node.name)
                return ret
            elif ret == -1:
                print '[%s] %s is missing' % (time.strftime(ISOTIMEFMT), self.node.name)
                return ret
            time.sleep(self.interval)

        print '[%s] Monitor thread of %s stopped' % (time.strftime(ISOTIMEFMT), self.node.ip)
        return 0

    def join(self, timeout=None):
        self.stopevent.set()
        threading.Thread.join(self, timeout)

threadlist = {}
set_global('localthread', threadlist)


def start_daemon_monitor(nodelist):
    for name, node in nodelist.items():
        if not node.status:
            #skip those not start daemon successfully
            continue
        if threadlist.has_key(name):
            #skip those already has a thread
            continue
        thread = Daemon_Monitor(node)
        #set sub-thread exits with main thread
        thread.setDaemon(True)
        thread.start()
        threadlist[name] = thread
#        print '[%s] Monitor thread for %s started' % (time.strftime(ISOTIMEFMT), node.name)

def stop_daemon_montitor():
    for name, thread in threadlist.items():
        thread.join()
        del threadlist[name]
#        print '[%s] Monitor thread for %s stopped' % (time.strftime(ISOTIMEFMT), name)
    return True

def start_daemon_monitor_s(node):
    if not node.status:
        #skip those not start daemon successfully
        return False
    if threadlist.has_key(name):
        #skip those already has a thread
        return True
    thread = Daemon_Monitor(node)
    #set sub-thread exits with main thread
    thread.setDaemon(True)
    thread.start()
    threadlist[name] = thread
    print '[%s] Monitor thread for %s started' % (time.strftime(ISOTIMEFMT), node.name)

def stop_daemon_monitor_s(nodename):
    if not threadlist.has_key(nodename):
        return True
    thread = threadlist[nodename]
    thread.join()
    del threadlist[nodename]
    print '[%s] Monitor thread for %s stopped' % (time.strftime(ISOTIMEFMT), nodename)


if __name__ == "__main__":
    print "Hello World";
