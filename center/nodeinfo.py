# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Apr 8, 2010 4:57:30 PM$"

import os, sys, time
import xmlrpclib


import node_perfinfo

import center_global

ISOTIMEFMT='%Y-%m-%d %X'

status_str = ['Stopped', 'Running', 'S3', 'S4', 'Error']

class Nodeinfo:
    """
    node domain info including:
    node(name, ip, uuid, mac) status
    xmlrpc(srv) log(fd)
    perf_data cpu_max mem_max
    Also node related functions
    """
    def __init__(self, name='defaultnode', ip='127.0.0.1',\
        uuid='0000', mac='00', mem_max=0, cpu_max=0):
        self.name = name
        self.ip = ip
        self.uuid = uuid
        self.mac = mac
        self.status = 0
        self.perf_info = node_perfinfo.NodePerfInfo(mem_max)
        self.mem_max = mem_max
        self.cpu_max = cpu_max
        self.port = 51000
        #set log output to stdout
        self.fp_log = sys.stdout
        self.fp_raw = sys.stdout
        self.fp_out = open('/dev/null', 'a+')

    def startlog(self, logfile='log', rawfile='raw'):
        """call when you need to write to logs instead of stdout"""
        #make data dir first
        data_loc = center_global.get_global('data_dir')
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
            print >> center_global.fp_clog, '[%s][%s] Failed to open %s' \
                % (time.strftime(ISOTIMEFMT), self.ip, self.log)
        self.raw = os.path.join(data_dir, rawfile)
        try:
            self.fp_raw = open(self.raw, 'a+')
        except:
            print >> center_global.fp_clog, '[%s][%s] Failed to open %s' \
                % (time.strftime(ISOTIMEFMT), self.ip, self.raw)
        self.out = os.path.join(data_dir, 'output')
        try:
            self.fp_out = open(self.out, 'a+')
            outputline = "timestamp,cpu_rate,cpu_iowait_rate,cpu_iowait_time,mem_ratio,mem_used,mem_total,pf_rate,disk_read(KB),disk_write(KB),net_recv(B),net_trans(B)"
            print >> self.fp_out, outputline
        except:
            print >> center_global.fp_clog, '[%s][%s] Failed to open %s' \
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

    def start(self, port=51000):
        self.port = port
        self.srvloc = 'http://%s:%d' % (self.ip, self.port)
        self.service = xmlrpclib.ServerProxy(self.srvloc)
        #self check
        self.status = 1
        #
        print >> self.fp_log, '[%s] Daemon started' % time.strftime(ISOTIMEFMT)
        return True


    def stop(self):
        try:
            self.status = 0
            self.service.stop_daemon()
            print >> self.fp_log, '[%s] Daemon stopped' % time.strftime(ISOTIMEFMT)
        except:
            pass

    def update_perf_info(self):
        data = self.service.get_perf_info()
        self.perf_info.update_cpu_rate(idle=data['cpu_idle'], total=data['cpu_total'],\
            iowait=data['cpu_iowait'])
        self.perf_info.mem_trace_push(mem_used=data['mem_used'])
        self.perf_info.pf_trace_push(data['pagefault'])
        self.perf_info.update_diskstat(data['diskstat'])
        self.perf_info.update_netstat(data['netstat'])
        outputline = '%f,%f,%f,%f,%d,%d,%d,%d,%d,%d' % (\
            self.perf_info.cpu_rate, self.perf_info.cpu_iowait_rate, self.perf_info.cpu_iowait_time,\
            self.perf_info.mem_ratio, self.perf_info.mem_used,\
            self.perf_info.pf_rate, self.perf_info.disk_read, self.perf_info.disk_write,\
            self.perf_info.net_recv, self.perf_info.net_trans)
        print >> self.fp_raw, '[%s] %s' % (time.strftime(ISOTIMEFMT), outputline)
        outputline = '%s,%.1f,%.1f,%.0f,%.1f,%d,%d,%d,%d,%d,%d' % (data['time'],\
            self.perf_info.cpu_rate, self.perf_info.cpu_iowait_rate, self.perf_info.cpu_iowait_time,\
            self.perf_info.mem_ratio, self.perf_info.mem_used / 1024,\
            self.perf_info.pf_rate, self.perf_info.disk_read, self.perf_info.disk_write,\
            self.perf_info.net_recv, self.perf_info.net_trans)
        print >> self.fp_out, outputline
        return self.status

#public structures

nodelist = {}
center_global.set_global('nodeinfo', nodelist)

def init_nodelist_from_file():
    filename = center_global.get_global('nodelist')
    fp = open(filename, 'r')
    lines = fp.readlines()
    fp.close()
    print >> center_global.fp_clog, center_global.syb_sep
    print >> center_global.fp_clog, 'Initial VM info object'
    for line in lines:
        if line[0] == '#':
            continue
        node_conf = line.strip().split(' ')
        print node_conf
        node = Nodeinfo(ip=node_conf[0], name=node_conf[1], uuid=node_conf[2], \
                    mac=node_conf[3], mem_max=int(node_conf[4]), cpu_max=int(node_conf[5]))
        nodelist[node.name] = node

def send_and_start_daemon():
    for name, node in nodelist.items():
        print >> center_global.fp_clog, center_global.syb_sep
        print >> center_global.fp_clog, '[%s] Starting node daemon on %s' %(time.strftime(ISOTIMEFMT), node.ip)
        cmdline = 'scp -r daemon %s:/root' % node.ip
        print >> center_global.fp_clog, '[%s] %s' %(time.strftime(ISOTIMEFMT), cmdline)
        os.system(cmdline)
        cmdline = 'ssh %s python /root/daemon/daemon_main.py -dl server' % node.ip
        print >> center_global.fp_clog, '[%s] %s' %(time.strftime(ISOTIMEFMT), cmdline)
        os.system(cmdline)
    print >> center_global.fp_clog, center_global.syb_sep

def init_vmlist_on_node():
    vm_nodelist = center_global.get_global('vm-nodelist')
#    vm_nodelist = 'vm_nodelist.lst'
#    print vm_nodelist
    fp = open(vm_nodelist, 'r')
    lines = fp.readlines()
    fp.close()
    #init vm lists
    vmlists = {}
    for name, node in nodelist.items():
        vmlists[name] = []
    for line in lines:
        if line[0] == '#':
            continue
        confinfo = line.split(':')
        vmlists[confinfo[0]].append(confinfo[1])
    for name, node in nodelist.items():
        node.service.update_vmlist_file(vmlists[name])


def start_all():
    for name, node in nodelist.items():
        #must use node.startlog() to make sure data dir is created
        node.startlog()
        print >> center_global.fp_clog, '[%s] Daemon Agent log of %s started' % (time.strftime(ISOTIMEFMT), name)
        node.start()

def stop_all():
    for name, node in nodelist.items():
        print >> center_global.fp_clog, center_global.syb_sep
        print >> center_global.fp_clog, '[%s] Stopping Daemon agent on %s' % (time.strftime(ISOTIMEFMT), name)
        node.stop()
        node.stoplog()
        print >> center_global.fp_clog, '[%s] Daemon Agent log of %s stopped' % (time.strftime(ISOTIMEFMT), name)
        try:
            node.service.stop_daemon()
        except:
            pass
        print >> center_global.fp_clog, '[%s] Daemon on %s stopped' % (time.strftime(ISOTIMEFMT), name)
    print >> center_global.fp_clog, center_global.syb_sep

def add_node(nodeinfo):
    nodeinit_filename = center_global.get_global('nodelist')
    fp = open(nodeinit_filename, 'a+')
    outputline = '%s %s %s %s %d %d' % (nodeinfo['ip'], nodeinfo['name'], nodeinfo['uuid'],\
                                          nodeinfo['mac'], nodeinfo['mem_max'], nodeinfo['cpu_max'])
    fp.write(outputline + '\n')
    fp.close()
    node = Nodeinfo(nodeinfo['ip'], nodeinfo['name'], nodeinfo['mac'], nodeinfo['uuid'],\
                nodeinfo['mem_max'], nodeinfo['cpu_max'])
    nodelist[nodeinfo['name']] = node

#    #start node daemon
#    print >> center_global.fp_clog, '[%s] Starting node daemon on %s' %(time.strftime(ISOTIMEFMT), vm.ip)
#    cmdline = 'scp -r daemon %s:/root' % vm.ip
#    print >> center_global.fp_clog, '[%s] %s' %(time.strftime(ISOTIMEFMT), cmdline)
#    os.system(cmdline)
#    cmdline = 'ssh %s python /root/daemon/daemon_main.py' % vm.ip
#    print >> center_global.fp_clog, '[%s] %s' %(time.strftime(ISOTIMEFMT), cmdline)
#    os.system(cmdline)
    #start vminfo
    node.startlog()
    node.start()

    print >> center_global.fp_clog, '[%s] Added new node %s' % (time.strftime(ISOTIMEFMT), str(outputline.split(' ')))
    return 0

def del_node(nodename):
    node = nodelist[nodename]
    #stop monitor thread
    threadlist = center_global.get_global('localthread')
    thread = threadlist[nodename]
    try:
        thread.join()
    except:
        pass
    #delete thread structure
    del threadlist[nodename]
    #stop daemon
    node.stop()
    #delete node structure
    del nodelist[nodename]
    #write to file
    nodeinit_filename = center_global.get_global('nodelist')
    fp = open(nodeinit_filename, 'w')
    for name, node in nodelist.items():
        outputline = '%s %s %s %s %d %d' % (node.ip, node.name, node.uuid, node.mac,\
                                            node.mem_max, node.cpu_max)
        fp.write(outputline + '\n')
    fp.close()
    print >> center_global.fp_clog, '[%s] Removed node %s' % (time.strftime(ISOTIMEFMT), nodename)
    return 0


if __name__ == "__main__":
#    print "Hello World";
#    #test 1
#    if sys.argv[1] == 'start_nodeinfo':
#        node = nodeinfo(name='testnode1', ip='192.168.122.14', mem_max=512, cpu_max=2)
##    node.startlog()
#        node.start()
#        node.update_perf_info()
#        time.sleep(1)
#        node.update_perf_info()
###    print node.perf_info.mem_ratio
###    print node.perf_info.mem_total
###    print node.perf_info.mem_used
###    print node.perf_info.mem_trace
###    print node.perf_info.cpu_rate
###    print node.perf_info.cpu_total
###    print node.perf_info.cpu_idle
###    print node.perf_info.pf_rate
###    print node.perf_info.pf_history
###    print node.perf_info.pf_trace
##
###    node.stop()
###    node.stoplog()
#
#    #test2
#    if sys.argv[1] == 'start_daemon':
#        init_nodelist_from_file()
#        send_and_start_daemon()
#    if sys.argv[1] == 'stop_daemon':
#        init_nodelist_from_file()
#        for name, node in nodelist.items():
#            node.stop()
#    if sys.argv[1] == 'start_mon':
#        init_nodelist_from_file()
#        for name, node in nodelist.items():
#            node.start()
#            node.update_perf_info()
#            time.sleep(1)
#            node.update_perf_info()

    init_nodelist_from_file()
    init_vmlist_on_node()
