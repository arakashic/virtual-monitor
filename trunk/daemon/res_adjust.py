# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Mar 24, 2010 2:14:31 PM$"

import os, sys, time

#import vminfo, perfinfo
import daemon_global

ISOTIMEFMT='%Y-%m-%d %X'

debug = True

#basic functions for VM memory adjustment
def set_vm_mem(vmname, new_mem_size):
    cmdline = 'xm mem-set %s %d' % (vmname, new_mem_size)
    try:
        os.system(cmdline)
    except:
        print >> daemon_global.fp_dlog, '[%s] Failed to set memory size for VM %s' % (time.strftime(ISOTIMEFMT), vmname)
        return False
    print >> daemon_global.fp_dlog, '[%s] Set memory size to %dMB for VM %s' % (time.strftime(ISOTIMEFMT),\
                                                      new_mem_size, vmname)
    return True

class AdjustModel1:
    """
    Old designed adjust model, monitoring pf and mem, do simple adjust
    """

    def get_new_mem_size(self, vm):
        new_mem_size = 0
        pf_flag = vm.perfinfo.is_pf_break_ave()
        memRatio = vm.perfinfo.mem_ratio
        if pf_flag and memRatio > 80:
            new_mem_size = vm.perfinfo.mem_total * (1 + 0.5)
        elif not pf_flag:
            diff = int(vm.perfinfo.mem_total * vm.perf_info.get_mem_peak_diff() / 100) / 2
            #print diff
            new_mem_size = vm.perfinfo.mem_total - diff
        else:
            new_mem_size = vm.perfinfo.mem_total
        return new_mem_size

class AdjustModel2:
    """
    cpu rate based algorithm model
    set enough mem for JVM use (typical is 200m for JVM)
    then adjust by little step to gain more avg pf

    be careful to those conversion from KB to MB
    """
    def __init__(self, vm, mem_jvm=200):
#        self.avg_pf_rate_history = 0
#        self.avg_pf_rate_now = 0
        self.avg_cpu_rate_history = 0
        self.avg_cpu_rate_now = 0
        self.mem_jvm=mem_jvm * 1024
        self.vm = vm

    def update(self):
        vm = self.vm
        #cpu rate
        if not self.avg_cpu_rate_history:
            self.avg_cpu_rate_history = vm.perf_info.avg_cpu_rate()
            self.avg_cpu_rate_now = self.avg_cpu_rate_history
        else:
            self.avg_cpu_rate_history = self.avg_cpu_rate_now
            self.avg_cpu_rate_now = vm.perf_info.avg_cpu_rate()
#        #pf rate
#        if not self.avg_pf_rate_history:
#            self.avg_pf_rate_history = vm.perf_info.avg_pf_rate()
#            self.avg_pf_rate_now = self.avg_pf_rate_history
#        else:
#            self.avg_pf_rate_history = self.avg_pf_rate_now
#            self.avg_pf_rate_now = vm.perf_info.avg_pf_rate()


    def is_need_adjust(self):
        """
        1. if cpu rate now and history both less than 15 percent, resize mem
        2. if cpu rate greater than 15 percent but less that 85 percent, resize mem
        3.
        """
        if self.avg_cpu_rate_history >= 15 and self.avg_cpu_rate_now < 15:
            return True
        elif int(self.avg_cpu_rate_now) in range(15, 85):
            return True
        else:
            return False


    def get_new_mem(self, add=50):
        """
        0. if cpu rate is less than 15%, set the mem to predefined minimal
        1. if free mem is less than jvm needed, set the free >= jvm need
        2. if more than the essential mem size, increase the mem by add
        3. never exceed the mem_max of vm
        R. return value in a tuple (alloc_size, expect_size),
           friendly to migration module
        """
        vm = self.vm
        mem_free = vm.perf_info.mem_total - vm.perf_info.mem_used
        #deallocation
        if self.avg_cpu_rate_now < 15:
            return (128, 128)
        #set to jvm level
        if mem_free < self.mem_jvm:
            #mem free less than jvm need
            new_mem_size = int((vm.perf_info.mem_used + self.mem_jvm) / 1024)
        else:
            #additional mem for buffering
            new_mem_size = int(vm.perf_info.mem_total / 1024 + add)
        #do not exceed the mem-max
        if new_mem_size > vm.mem_max:
            return (vm.mem_max, new_mem_size)
        else:
            return (new_mem_size, new_mem_size)

    def print_info(self):
        print >> daemon_global.fp_dlog, '[%s] %s %d, %d' % (time.strftime(ISOTIMEFMT),\
            self.vm.name, self.avg_cpu_rate_history, self.avg_cpu_rate_now)

            

class AdjustModel3:
    """
    cpu rate based algorithm model
    set enough mem for JVM use (typical is 200m for JVM)
    then adjust by little step to gain more avg pf
    consider the iowait time of cpu

    be careful to those conversion from KB to MB
    """
    def __init__(self, vm, mem_jvm=200):
#        self.avg_pf_rate_history = 0
#        self.avg_pf_rate_now = 0
        self.avg_cpu_rate_history = 0
        self.avg_cpu_rate_now = 0
        self.avg_cpu_iowait_rate_history = 0
        self.avg_cpu_iowait_rate_now = 0
        self.mem_jvm=mem_jvm * 1024
        self.vm = vm
        #intensive specify signs
        self.cpu_intensive = False
        self.mem_intensive = False
        self.io_intensive = False
        #allocation signs
        self.jvm_alloc = False
        self.add_alloc_attemp = False

    def update(self):
        vm = self.vm
        #cpu rate
        if not self.avg_cpu_rate_history:
            self.avg_cpu_rate_history = vm.perf_info.avg_cpu_rate()
            self.avg_cpu_rate_now = self.avg_cpu_rate_history
            self.avg_cpu_iowait_rate_history = vm.perf_info.avg_cpu_iowait_rate()
            self.avg_cpu_iowait_rate_now = self.avg_cpu_iowait_rate_history
        else:
            self.avg_cpu_rate_history = self.avg_cpu_rate_now
            self.avg_cpu_rate_now = vm.perf_info.avg_cpu_rate()
            self.avg_cpu_iowait_rate_history = self.avg_cpu_iowait_rate_now
            self.avg_cpu_iowait_rate_now = vm.perf_info.avg_cpu_iowait_rate()
#        #pf rate
#        if not self.avg_pf_rate_history:
#            self.avg_pf_rate_history = vm.perf_info.avg_pf_rate()
#            self.avg_pf_rate_now = self.avg_pf_rate_history
#        else:
#            self.avg_pf_rate_history = self.avg_pf_rate_now
#            self.avg_pf_rate_now = vm.perf_info.avg_pf_rate()


    def is_need_adjust(self):
        """
        1. if cpu rate now and history both less than 15 percent, resize mem
        2. if cpu rate greater than 15 percent but less that 85 percent, resize mem
        3. if cpu iowait rate kept higher than 45% for 20sec (2 period), try to resize mem
           when attempted and no effect, give up and seeking migration
        """
#        return False
        if self.avg_cpu_iowait_rate_history > 45 and self.avg_cpu_iowait_rate_now > 45:
            self.io_intensive = True
        else:
            self.io_intensive = False
            
        if int(self.avg_cpu_rate_history) not in range(15, 85):
            return True
        elif int(self.avg_cpu_rate_now) in range(15, 85):
            if self.avg_cpu_rate_now > self.avg_cpu_rate_history:
                return True
            else:
#                self.add_alloc_attemp = False
                return False
        else:
            return False


    def get_new_mem(self, add=50):
        """
        0. if cpu rate is less than 15%, set the mem to predefined minimal
        1. if free mem is less than jvm needed, set the free >= jvm need
        2. if more than the essential mem size, increase the mem by add
        3. never exceed the mem_max of vm
        4. set jvm_alloc sign when allocated jvm mem
        5. set add_alloc_attemp sign, means add allocation attempted
        R. return value in a tuple (alloc_size, expect_size),
           friendly to migration module
        """
        vm = self.vm
        mem_free = vm.perf_info.mem_total - vm.perf_info.mem_used
        #deallocation
        if self.avg_cpu_rate_now < 15:
            self.cpu_intensive = False
            self.mem_intensive = False
            self.io_intensive = False
            self.jvm_alloc = False
            self.add_alloc_attemp = False
            return (128, 128)
        #set to jvm level
        if not jvm_alloc and mem_free < self.mem_jvm:
            #mem free less than jvm need
            new_mem_size = int((vm.perf_info.mem_used + self.mem_jvm) / 1024)
            self.jvm_alloc = True
        else:
            #additional mem for buffering
            new_mem_size = int(vm.perf_info.mem_total / 1024 + add)
            self.add_alloc_attemp = True
        #do not exceed the mem-max
        if new_mem_size > vm.mem_max:
            return (vm.mem_max, new_mem_size)
        else:
            return (new_mem_size, new_mem_size)

    def print_info(self):
        print >> daemon_global.fp_dlog, '[%s] %s %d, %d, %d, %d' % (time.strftime(ISOTIMEFMT),\
            self.vm.name, self.avg_cpu_rate_history, self.avg_cpu_rate_now,\
            self.avg_cpu_iowait_rate_history, self.avg_cpu_iowait_rate_now)
#        print >> daemon_global.fp_dlog, '%s %s' % (self.vm.name, str(self.vm.perf_info.cpu_iowait_trace))


if __name__ == "__main__":
    print "Hello World";
