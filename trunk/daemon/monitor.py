# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Mar 22, 2010 9:10:15 PM$"

import os, time
import threading

import vminfo, res_adjust
from daemon_global import set_global, get_global, fp_dlog

#import stat.stats


ISOTIMEFMT='%Y-%m-%d %X'

class AgentHeartBeat(threading.Thread):
    """
    heart beat monitor for all agents to check if agent is online
    default period time of checking is 30 seconds
    """
    def __init__(self, VMlist, interval=30):
        threading.Thread.__init__(self)
        self.VMlist = VMlist
        self.interval = interval

    def run(self):
        self.stopevent = threading.Event()
        while not self.stopevent.isSet():
            for name, vm in self.VMlist.items():
                try:
                    vm.service.heart_beat()
                except:
                    print >> fp_dlog, '[%s] VM %s(%s) is lost' % (time.strftime(ISOTIMEFMT), name, vm.ip)
        return 0

    def join(self, timeout = None):
        self.stopevent.set()
        threading.Thread.join(self, timeout)

class VM_Monitor(threading.Thread):
    def __init__(self, vm, interval=1):
        threading.Thread.__init__(self)
        self.vm = vm
        self.interval = interval
#        self.stopevent = threading.Event()

    def run(self):
        self.stopevent = threading.Event()
        ret = self.vm.update_perf_info()
        if ret == -2:
            print >> fp_dlog, '[%s] %s is missing' % (time.strftime(ISOTIMEFMT), self.vm.name)
            return ret
        elif ret == -1:
            print >> fp_dlog, '[%s] %s is migrated' % (time.strftime(ISOTIMEFMT), self.vm.name)
            return ret
        print >> fp_dlog, '[%s] Monitor thread of %s started' % (time.strftime(ISOTIMEFMT), self.vm.ip)
        while not self.stopevent.isSet( ):

            ret = self.vm.update_perf_info()
            #exceptions
            if ret == -2:
                print >> fp_dlog, '[%s] %s is missing' % (time.strftime(ISOTIMEFMT), self.vm.name)
                return ret
            elif ret == -1:
                print >> fp_dlog, '[%s] %s is missing' % (time.strftime(ISOTIMEFMT), self.vm.name)
                return ret
            time.sleep(self.interval)

        print >> fp_dlog, '[%s] Monitor thread of %s stopped' % (time.strftime(ISOTIMEFMT), self.vm.ip)
        return 0

    def join(self, timeout=None):
        self.stopevent.set()
        threading.Thread.join(self, timeout)

class AdjustThread(threading.Thread):
    def __init__(self, vminfo_list, interval=10):
        threading.Thread.__init__(self)
        self.interval = interval
        self.vminfo_list = vminfo_list
        self.adjust_model = []

        for name, vm in self.vminfo_list.items():
            #change this when changing AdjustModel
            model = res_adjust.AdjustModel2(vm)
            model.update()
            self.adjust_model.append(model)

    def run(self):
        self.stopevent = threading.Event()
        while not self.stopevent.isSet():
#            for name, vm in self.vminfo_list.items():
#                print >> fp_dlog, '[%s] %s Avg. on pf_rate: %d' % (time.strftime(ISOTIMEFMT), name,\
#                    vm.perf_info.avg_pf_rate())
            #adjust model
            for model in self.adjust_model:
                model.update()
                print >> fp_dlog, '[%s] %s %d, %d' % (time.strftime(ISOTIMEFMT),\
                        model.vm.name, model.avg_cpu_rate_history, model.avg_cpu_rate_now)
                if model.is_need_adjust():
                    new_mem = model.get_new_mem()
                    print >> fp_dlog, '[%s] %s True %dMB, %dMB' % (time.strftime(ISOTIMEFMT),\
                        model.vm.name, new_mem[0], new_mem[1])
                    res_adjust.set_vm_mem(model.vm.name, new_mem[0])


            time.sleep(self.interval)
            print >> fp_dlog, ' '

    def join(self, timeout=None):
        self.stopevent.set()
        threading.Thread.join(self, timeout)
        
threadlist = {}
set_global('localthread', threadlist)


def start_agent_monitor(vmlist):
    for name, vm in vmlist.items():
        if not vm.status:
            #skip those not start agent successfully
            continue
        if threadlist.has_key(name):
            #skip those already has a thread
            continue
        thread = VM_Monitor(vm)
        #set sub-thread exits with main thread
        thread.setDaemon(True)
        thread.start()
        threadlist[name] = thread
#        print >> fp_dlog, '[%s] Monitor thread for %s started' % (time.strftime(ISOTIMEFMT), vm.name)

def stop_agent_montitor():
    for name, thread in threadlist.items():
        thread.join()
        del threadlist[name]
#        print >> fp_dlog, '[%s] Monitor thread for %s stopped' % (time.strftime(ISOTIMEFMT), name)
    return True

def start_agent_monitor_s(vm):
    if not vm.status:
        #skip those not start agent successfully
        return False
    if threadlist.has_key(name):
        #skip those already has a thread
        return True
    thread = VM_Monitor(vm)
    #set sub-thread exits with main thread
    thread.setDaemon(True)
    thread.start()
    threadlist[name] = thread
    print >> fp_dlog, '[%s] Monitor thread for %s started' % (time.strftime(ISOTIMEFMT), vm.name)

def stop_agent_monitor_s(vmname):
    if not threadlist.has_key(vmname):
        return True
    thread = threadlist[vmname]
    thread.join()
    del threadlist[vmname]
    print >> fp_dlog, '[$s] Monitor thread for %s stopped' % (time.strftime(ISOTIMEFMT), vmname)

def start_adjust_thread():
    vminfo_list = get_global('vminfo')
    adjust_thread = AdjustThread(vminfo_list, 10)
    adjust_thread.setDaemon(True)
    adjust_thread.start()
    threadlist['adjust_thread'] = adjust_thread
    print >> fp_dlog, '[%s] Adjust thread started' % time.strftime(ISOTIMEFMT)


if __name__ == "__main__":
    print "Hello World";
