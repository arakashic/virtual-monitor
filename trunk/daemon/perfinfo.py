# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Mar 22, 2010 4:54:21 PM$"


class PerfInfo:
    """
    contains all the essential peformance info of vm domain including
    cpu(total, idle, rate) mem(total, used, rate) pf(rate) diskstat(rd, wr)
    netstat(trans, recv)
    others is structures for info tracing
    """
    def __init__(self):
        #basics vars
        self.cpu_idle = 0.0
        self.cpu_total = 0.0
        self.cpu_iowait = 0.0
        self.cpu_rate = 0.0
        self.cpu_iowait_rate = 0.0
        self.cpu_iowait_time = 0.0
        #mem
        self.mem_used = 0.0
        self.mem_total = 0.0
        self.mem_ratio = 0.0
        #pf
        self.pf_rate = 0
        #disk and net stat
        self.disk_history = {}
        self.net_history = {}
        self.disk_read = 0
        self.disk_write = 0
        self.net_recv = 0
        self.net_trans = 0
        #trace control
        self.switch = {'cpu_trace':1,\
                       'mem_trace':1,\
                       'pf_trace':1,\
                       'disk_trace':1,\
                       'net_trace':1}
        #perf trace
        self.cpu_trace_size = 10
        self.cpu_trace = []
        self.cpu_iowait_trace_size = 10
        self.cpu_iowait_trace = []

        self.mem_trace_size = 10
        self.mem_trace = []

        self.pf_trace_size = 10
        self.pf_trace = []
        self.pf_history = 0

    def mem_trace_push(self, mem_total, mem_used):
        mem = mem_used / mem_total * 100
        self.mem_used = mem_used
        self.mem_total = mem_total
        if self.mem_ratio == mem:
            return 0
        self.mem_ratio = mem
        #mem trace
        if self.switch['mem_trace']:
            if len(self.mem_trace) == self.mem_trace_size:
                self.mem_trace.pop(0)
            self.mem_trace.append(mem)

    def pf_trace_push(self, pf):
        if self.pf_history == 0:
            self.pf_history = pf
            return 0
        diff = pf - self.pf_history
        self.pf_history = pf
        self.pf_rate = diff
        #pf trace
        if self.switch['pf_trace']:
            if len(self.pf_trace) == self.pf_trace_size:
                self.pf_trace.pop(0)
            self.pf_trace.append(diff)

    def update_cpu_rate(self, idle, total, iowait):
        if self.cpu_idle == 0 or self.cpu_total == 0:
            self.cpu_idle = idle
            self.cpu_total = total
            self.cpu_iowait = iowait
            return 0
        try:
            self.cpu_rate = (1 - ((idle - self.cpu_idle) / (total - self.cpu_total))) * 100
        except:
            pass
        self.cpu_iowait_time = (iowait - self.cpu_iowait)
        cpu_busy_time = (total - self.cpu_total) - (idle - self.cpu_idle)
        try:
            self.cpu_iowait_rate = (self.cpu_iowait_time / cpu_busy_time) * 100
        except:
            pass
        self.cpu_idle = idle
        self.cpu_total = total
        self.cpu_iowait = iowait
        #cpu trace
        if self.switch['cpu_trace'] == 1:
            if len(self.cpu_trace) == self.cpu_trace_size:
                self.cpu_trace.pop(0)
            self.cpu_trace.append(self.cpu_rate)
            if len(self.cpu_iowait_trace) == self.cpu_iowait_trace_size:
                self.cpu_iowait_trace.pop(0)
            self.cpu_iowait_trace.append(self.cpu_iowait_rate)

        return self.cpu_rate

    def update_diskstat(self, diskstat):
        """calculate disk IO in kBs"""

        if len(self.disk_history) == 0:
            self.disk_history = diskstat
        else:
            self.disk_read = (diskstat['sectors_read'] - self.disk_history['sectors_read']) / 2
            self.disk_write = (diskstat['sectors_written'] - self.disk_history['sectors_written']) / 2
            self.disk_history = diskstat

    def update_netstat(self, netstat):
        """calculate net IO in kBs"""
        
        if len(self.net_history) == 0:
            self.net_history = netstat
        else:
            self.net_recv = (netstat['recv_bytes'] - self.net_history['recv_bytes']) /1024
            self.net_trans = (netstat['trans_bytes'] - self.net_history['trans_bytes']) / 1024
            self.net_history = netstat

    def is_mem_reduce(self):
        p = self.mem_trace_head
        for n in range(0,self.mem_trace_size - 1):
            i = (p + n) % self.mem_trace_size
            j = (i + 1) % self.mem_trace_size
            if (self.mem_trace[i] - self.mem_trace[j]) <= 0:
                return False
        return True

    def is_pf_break_ave(self):
        count = len(self.pf_trace)
        if count < 10:
            return False
        ave = 0
        for i in self.pf_trace:
            ave += i
        ave /= count
        #this will affect the sensitivity on page fault rate
        if self.pa_rate > (2*ave):
            return True
        else:
            False

    def avg_cpu_rate(self):
        count = len(self.cpu_trace)
        if not count:
            return float(0)
        avg = float(0)
        for i in self.cpu_trace:
            avg += i
        avg /= count
        return avg

    def avg_cpu_iowait_rate(self):
        count = len(self.cpu_iowait_trace)
        if not count:
#            print count
            return float(0)
        avg = float(0)
        for i in self.cpu_iowait_trace:
            avg += i
        avg /= count
#        print avg
        return avg

    def avg_pf_rate(self):
        count = len(self.pf_trace)
        if not count:
            return 0
        avg = 0
        for i in self.pf_trace:
            avg += i
        avg /= count
        return avg

    def get_mem_peak_diff(self):
        if len(self.mem_trace) <= 0:
            return 0
        max = self.mem_trace[0]
        min = self.mem_trace[0]
        for mem in self.mem_trace:
            if mem > max:
                max = mem
            if mem < min:
                min = mem
        return max - min


if __name__ == "__main__":
    print "Hello World";
    perf = PerfInfo()
    perf.mem_trace_push(100.0, 90.0)
    print perf.mem_total
    print perf.mem_used
    print perf.mem_ratio
    print str(perf.mem_trace)
