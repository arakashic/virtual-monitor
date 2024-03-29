import cluster_resource
# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Apr 12, 2010 2:39:16 PM$"

import os, time
import threading

import nodeinfo
import center_global
import cluster_resource

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
                    print >> center_global.fp_clog, '[%s] Daemon %s(%s) is lost' % (time.strftime(ISOTIMEFMT), name, vm.ip)
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
        if not ret:
            print >> center_global.fp_clog, '[%s] %s is missing' % (time.strftime(ISOTIMEFMT), self.node.name)
            return ret
        print >> center_global.fp_clog, '[%s] Monitor thread of %s started' % (time.strftime(ISOTIMEFMT), self.node.ip)
        while not self.stopevent.isSet( ):

            ret = self.node.update_perf_info()
            #exceptions
            if not ret:
                print >> center_global.fp_clog, '[%s] %s is missing' % (time.strftime(ISOTIMEFMT), self.node.name)
                return ret
            time.sleep(self.interval)

        print >> center_global.fp_clog, '[%s] Monitor thread of %s stopped' % (time.strftime(ISOTIMEFMT), self.node.ip)
        return 0

    def join(self, timeout=None):
        self.stopevent.set()
        threading.Thread.join(self, timeout)

class ResourceAssessor_Thread(threading.Thread):
    def __init__(self, res_assessor, interval=5):
        threading.Thread.__init__(self)
        self.res_assessor = res_assessor
        self.interval = interval

        def run(self):
            self.stopevent = threading.Event()
            ret = self.res_assessor.update()
            if not ret:
                print >> center_global.fp_clog, '[%s] Resource Assessor Error' % time.strftime(ISOTIMEFMT)
                return ret
            print >> center_global.fp_clog, '[%s] 2Resource Assessor started' % time.strftime(ISOTIMEFMT)
            while not self.stopevent.isSet():
                ret = self.res_assessor.update()
                self.res_assessor.output()
                if not ret:
                    print >> center_global.fp_clog, '[%s] Resource Assessor Error' % time.strftime(ISOTIMEFMT)
                    return ret
                time.sleep(self.interval)
            print >> center_global.fp_clog, '[%s] Resource Assessor stopped' % time.strftime(ISOTIMEFMT)
            return 0

        def join(self, timeout=None):
            self.stopevent.set()
            threading.Thread.join(self.timeout)
            

threadlist = {}
center_global.set_global('localthread', threadlist)


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
#        print >> center_global.fp_clog, '[%s] Monitor thread for %s started' % (time.strftime(ISOTIMEFMT), node.name)

def stop_daemon_montitor():
    for name, thread in threadlist.items():
        thread.join()
        del threadlist[name]
#        print >> center_global.fp_clog, '[%s] Monitor thread for %s stopped' % (time.strftime(ISOTIMEFMT), name)
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
    print >> center_global.fp_clog, '[%s] Monitor thread for %s started' % (time.strftime(ISOTIMEFMT), node.name)

def stop_daemon_monitor_s(nodename):
    if not threadlist.has_key(nodename):
        return True
    thread = threadlist[nodename]
    thread.join()
    del threadlist[nodename]
    print >> center_global.fp_clog, '[%s] Monitor thread for %s stopped' % (time.strftime(ISOTIMEFMT), nodename)

def start_resource_assessor():
    res_assessor = cluster_resource.NodeResourceAssessor()
    center_global.set_global('res_assessor', res_assessor)
    thread = ResourceAssessor_Thread(res_assessor)
    thread.setDaemon(True)
    thread.start()
    threadlist['res_assessor'] = thread
    print >> center_global.fp_clog, '[%s] Resource Assessor started' % time.strftime(ISOTIMEFMT)

def stop_resource_assessor():
    if not threadlist.has_key('res_assessor'):
        return True
    thread = threadlist['res_assessor']
    thread.join()
    del threadlist['res_assessor']
    print >> center_global.fp_clog, '[%s] Resource Assessor stopped' % time.strftime(ISOTIMEFMT)


if __name__ == "__main__":
    print "Hello World";
