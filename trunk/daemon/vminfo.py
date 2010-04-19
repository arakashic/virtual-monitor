# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Mar 22, 2010 5:15:54 PM$"

import os, sys, time
import xmlrpclib


import perfinfo

#from daemon_global import daemon_global.get_global, daemon_global.set_global, daemon_global.fp_dlog
import daemon_global

ISOTIMEFMT='%Y-%m-%d %X'

class VMinfo:
    """
    VM domain info including:
    vm(name, ip, uuid, mac) status
    xmlrpc(srv) log(fd)
    perf_data vcpu_max mem_max
    Also VM related functions
    """
    def __init__(self, name='default', ip='127.0.0.1',\
        uuid='0000', mac='00', mem_max=0, vcpu_max=0):
        self.name = name
        self.ip = ip
        self.uuid = uuid
        self.mac = mac
        self.status = 0
        self.perf_info = perfinfo.PerfInfo()
        self.mem_max = mem_max
        self.vcpu_max = vcpu_max
        #set log output to stdout
        self.fp_log = sys.stdout
        self.fp_raw = sys.stdout
        self.fp_out = open('/dev/null', 'a+')

    def startlog(self, logfile='log', rawfile='raw'):
        """call when you need to write to logs instead of stdout"""
        #make data dir first
        data_loc = daemon_global.get_global('data_dir')
        data_loc = 'data'
        data_dir = os.path.join(data_loc, self.ip)
        try:
            os.mkdir(data_dir)
        except:
            pass
        #open log files
        self.log = os.path.join(data_dir, logfile)
        try:
            self.fp_log = open(self.log, 'a+')
        except:
            print >> daemon_global.fp_dlog, '[%s][%s] Failed to open %s' \
                % (time.strftime(ISOTIMEFMT), self.ip, self.log)
        self.raw = os.path.join(data_dir, rawfile)
        try:
            self.fp_raw = open(self.raw, 'a+')
        except:
            print >> daemon_global.fp_dlog, '[%s][%s] Failed to open %s' \
                % (time.strftime(ISOTIMEFMT), self.ip, self.raw)
        self.out = os.path.join(data_dir, 'output')
        try:
            self.fp_out = open(self.out, 'a+')
            outputline = "timestamp,cpu_rate,cpu_iowait_rate,cpu_iowait_time,mem_ratio,mem_used,mem_total,pf_rate,disk_read(KB),disk_write(KB),net_recv(B),net_trans(B)"
            print >> self.fp_out, outputline
        except:
            print >> daemon_global.fp_dlog, '[%s][%s] Failed to open %s' \
                % (time.strftime(ISOTIMEFMT), self.ip, self.out)
        return True

    def stoplog(self):
        try:
            self.fp_log.close()
            self.fp_raw.close()
            self.fp_out.close()
        except:
            pass
        self.fp_log = sys.stdout
        self.fp_raw = sys.stdout

    def start(self, port=8080):
        self.port = port
        self.srvloc = 'http://%s:%d' % (self.ip, self.port)
        self.service = xmlrpclib.ServerProxy(self.srvloc)
        #self check
        self.status = 1
        #
        print >> self.fp_log, '[%s] Agent started' % time.strftime(ISOTIMEFMT)
        return True


    def stop(self):
        if not self.status:
            return True
        try:
            self.status = 0
            self.service.stop_agent()
            print >> self.fp_log, '[%s] Agent stopped' % time.strftime(ISOTIMEFMT)
        except:
            pass
        self.stoplog()
        return True

    def update_perf_info(self):
        data = self.service.get_perf_info()
        self.perf_info.update_cpu_rate(idle=data['cpu_idle'], total=data['cpu_total'],\
            iowait=data['cpu_iowait'])
        self.perf_info.mem_trace_push(mem_total=data['mem_total'], mem_used=data['mem_used'])
        self.perf_info.pf_trace_push(data['pagefault'])
        self.perf_info.update_diskstat(data['diskstat'])
        self.perf_info.update_netstat(data['netstat'])
        outputline = '%f,%f,%f,%f,%d,%d,%d,%d,%d,%d' % (\
            self.perf_info.cpu_rate, self.perf_info.cpu_iowait_rate, self.perf_info.cpu_iowait_time,\
            self.perf_info.mem_ratio, self.perf_info.mem_used,\
            self.perf_info.pf_rate, self.perf_info.disk_read, self.perf_info.disk_write,\
            self.perf_info.net_recv, self.perf_info.net_trans)
        print >> self.fp_raw, '[%s] %s' % (time.strftime(ISOTIMEFMT), outputline)
        outputline = '%s,%.1f,%.1f,%.0f,%.1f,%d,%d,%d,%d,%d,%d,%d' % (data['time'],\
            self.perf_info.cpu_rate, self.perf_info.cpu_iowait_rate, self.perf_info.cpu_iowait_time,\
            self.perf_info.mem_ratio, self.perf_info.mem_used / 1024, self.perf_info.mem_total / 1024,\
            self.perf_info.pf_rate, self.perf_info.disk_read, self.perf_info.disk_write,\
            self.perf_info.net_recv, self.perf_info.net_trans)
        print >> self.fp_out, outputline
        return self.status

    #functions for resource adjustment
#    def set_mem(self, new_mem_size):
#        cmdline = 'xm mem-set %s %d' % (self.name, new_mem_size)

#public structures

VMlist = {}
daemon_global.set_global('vminfo', VMlist)

def init_vmlist_from_file():
    filename = daemon_global.get_global('vmlist')
    fp = open(filename, 'r')
    lines = fp.readlines()
    fp.close()
    print >> daemon_global.fp_dlog, daemon_global.syb_sep
    print >> daemon_global.fp_dlog, 'Initial VM info object'
    for line in lines:
        if line[0] == '#':
            continue
        vm_conf = line.strip().split(' ')
        print >> daemon_global.fp_dlog, vm_conf
        vm = VMinfo(ip=vm_conf[0], name=vm_conf[1], uuid=vm_conf[2], \
                    mac=vm_conf[3], mem_max=int(vm_conf[4]), vcpu_max=int(vm_conf[5]))
        VMlist[vm.name] = vm

def send_and_start_agent():
    for name, vm in VMlist.items():
        print >> daemon_global.fp_dlog, daemon_global.syb_sep
        print >> daemon_global.fp_dlog, '[%s] Starting VM agent on %s' %(time.strftime(ISOTIMEFMT), vm.ip)
        cmdline = 'scp -r agent %s:/root' % vm.ip
        print >> daemon_global.fp_dlog, '[%s] %s' %(time.strftime(ISOTIMEFMT), cmdline)
        os.system(cmdline)
        cmdline = 'ssh %s python /root/agent/agent_main.py' % vm.ip
        print >> daemon_global.fp_dlog, '[%s] %s' %(time.strftime(ISOTIMEFMT), cmdline)
        os.system(cmdline)
    print >> daemon_global.fp_dlog, daemon_global.syb_sep

def start_all():
    for name, vm in VMlist.items():
        #must use vm.startlog() to make sure data dir is created
        vm.startlog()
        print >> daemon_global.fp_dlog, '[%s] Agent log of %s started' % (time.strftime(ISOTIMEFMT), name)
        vm.start()

def stop_all():
    for name, vm in VMlist.items():
        print >> daemon_global.fp_dlog, daemon_global.syb_sep
        print >> daemon_global.fp_dlog, '[%s] Stopping VM agent on %s' % (time.strftime(ISOTIMEFMT), name)
        vm.stop()
        vm.stoplog()
        print >> daemon_global.fp_dlog, '[%s] Agent log of %s stopped' % (time.strftime(ISOTIMEFMT), name)
        try:
            vm.service.stop_agent()
        except:
            pass
        print >> daemon_global.fp_dlog, '[%s] Agent on %s stopped' % (time.strftime(ISOTIMEFMT), name)
    print >> daemon_global.fp_dlog, daemon_global.syb_sep

def add_vm(vminfo):
    vminit_filename = daemon_global.get_global('vmlist')
    fp = open(vminit_filename, 'a+')
    outputline = '%s %s %s %s %d %d' % (vminfo['ip'], vminfo['name'], vminfo['uuid'],\
                                          vminfo['mac'], vminfo['mem_max'], vminfo['vcpu_max'])
    fp.write(outputline + '\n')
    fp.close()
    vm = VMinfo(vminfo['ip'], vminfo['name'], vminfo['mac'], vminfo['uuid'],\
                vminfo['mem_max'], vminfo['vcpu_max'])
    VMlist[vminfo['name']] = vm

#    #start vm agent
#    print >> daemon_global.fp_dlog, '[%s] Starting VM agent on %s' %(time.strftime(ISOTIMEFMT), vm.ip)
#    cmdline = 'scp -r agent %s:/root' % vm.ip
#    print >> daemon_global.fp_dlog, '[%s] %s' %(time.strftime(ISOTIMEFMT), cmdline)
#    os.system(cmdline)
#    cmdline = 'ssh %s python /root/agent/agent_main.py' % vm.ip
#    print >> daemon_global.fp_dlog, '[%s] %s' %(time.strftime(ISOTIMEFMT), cmdline)
#    os.system(cmdline)
    #start vminfo
    vm.startlog()
    vm.start()

    print >> daemon_global.fp_dlog, daemon_global.syb_sep
    print >> daemon_global.fp_dlog, '[%s] Added new VM %s' % (time.strftime(ISOTIMEFMT), str(outputline.split(' ')))
    print >> daemon_global.fp_dlog, '[%s] Config: %s' % (time.strftime(ISOTIMEFMT), str(vminfo))
    print >> daemon_global.fp_dlog, daemon_global.syb_sep
    return 0

def del_vm(vmname):
    vm = VMlist[vmname]
    #stop monitor thread
    threadlist = daemon_global.get_global('localthread')
    try:
        thread = threadlist[vmname]
        thread.join()
        del threadlist[vmname]
    except:
        pass
    #delete thread structure
    #stop agent
    vm.stop()
    #delete vm structure
    del VMlist[vmname]
    #write to file
    vminit_filename = daemon_global.get_global('vmlist')
    fp = open(vminit_filename, 'w')
    for name, vm in VMlist.items():
        outputline = '%s %s %s %s %d %d' % (vm.ip, vm.name, vm.uuid, vm.mac,\
                                            vm.mem_max, vm.vcpu_max)
        fp.write(outputline + '\n')
    fp.close()

    print >> daemon_global.fp_dlog, daemon_global.syb_sep
    print >> daemon_global.fp_dlog, '[%s] Removed VM %s' % (time.strftime(ISOTIMEFMT), vmname)
    print >> daemon_global.fp_dlog, daemon_global.syb_sep
    return 0

def do_migrate(vmname, destip, destport):
    print >> daemon_global.fp_dlog, daemon_global.syb_sep
    #set status to migrating and stop monitoring
    writeLog('Mirgrating ' + vmname + ' to ' + destip)
    print >> daemon_global.fp_dlog, '[%s] Migrating %s %d' % (time.strftime(ISOTIMEFMT),\
        vmname, destip, destport)
    vm = VMlist[vmname]
    #stop adjust model

    #stop monitor thread
    threadlist = get_global('localthread')
    try:
        thread = threadlist[vmname]
        thread.join()
        del threadlist[vmname]
    except:
        pass
    #stop vminfo
#    vm.status = -1
#    vm.stop()
    #call migrate
    cmdline = 'xm migrate -l %s %s' % (vmname, destip)
    print daemon_global.fp_dlog, '[%s] %s' % (time.strftime(ISOTIMEFMT), cmdline)
    ret = os.system(cmdline)
    if ret:
        #when failed return error
        print daemon_global.fp_dlog, '[%s] Failed when migrating %s to %s' % (vmname, destip)
        vm.status = -2
    #stop vminfo
    vm.stop()
    #when success del current vm and create new one
    print 'done'
    vminfo = {}
    vminfo['name'] = vm.name
    vminfo['ip'] = vm.ip
    vminfo['uuid'] = vm.uuid
    vminfo['mac'] = vm.mac
    vminfo['mem'] = vm.max_mem
    vminfo['vcpu'] = vm.max_vcpu
    #use directly transfer when has key
    srv_loc = 'http://%s:%d' % (destip, destport)
    service = xmlrpclib.ServerProxy(srv_loc)
    try:
        service.start_new_vm(vminfo)
    except:
        pass
    del_vm(vmname)
#    centerip = get_global('center')
#    if centerip != None:
#        loc = 'http://' + centerip + str(get_global('centerport'))
#        service = xmlrpclib.ServerProxy(loc)
#        try:
#            service.TransferVMInfo(vminfo, destip, destport)
#        except:
#            pass
#    else:
#        loc = 'http://' + destip + ':' + str(destport)
#        service = xmlrpclib.ServerProxy(loc)
#        try:
#            service.StartNewVM(vminfo)
#        except:
#            pass
#    #del current
#    VM_info.del_VM(vmname)
    return True


if __name__ == "__main__":
    print "Hello World";
    #test 1
    if sys.argv[1] == 'start_vminfo':
        vm = VMinfo(name='testvm1', ip='192.168.122.14', mem_max=512, vcpu_max=2)
#    vm.startlog()
        vm.start()
        vm.update_perf_info()
        time.sleep(1)
        vm.update_perf_info()
##    print vm.perf_info.mem_ratio
##    print vm.perf_info.mem_total
##    print vm.perf_info.mem_used
##    print vm.perf_info.mem_trace
##    print vm.perf_info.cpu_rate
##    print vm.perf_info.cpu_total
##    print vm.perf_info.cpu_idle
##    print vm.perf_info.pf_rate
##    print vm.perf_info.pf_history
##    print vm.perf_info.pf_trace
#
##    vm.stop()
##    vm.stoplog()

    #test2
    if sys.argv[1] == 'start_agent':
        init_vmlist_from_file()
        send_and_start_agent()
    if sys.argv[1] == 'stop_agent':
        init_vmlist_from_file()
        for name, vm in VMlist.items():
            vm.stop()
    if sys.argv[1] == 'start_mon':
        init_vmlist_from_file()
        for name, vm in VMlist.items():
            vm.start()
            vm.update_perf_info()
            time.sleep(1)
            vm.update_perf_info()
