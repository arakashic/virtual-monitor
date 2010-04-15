# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Mar 24, 2010 4:42:39 PM$"

import os, sys, time
import fcntl, socket, struct
import SimpleXMLRPCServer

import monitor, vminfo, daemon_agent
from daemon_global import get_global, cleanup_exit, fp_dlog

ISOTIMEFMT='%Y-%m-%d %X'

#basic control service
def stop_daemon():
    stop_monitor()
    stop_vminfo()
    print >> fp_dlog, '[%s] Stopping daemon' % time.strftime(ISOTIMEFMT)
    server.server_close()
    cleanup_exit()

def stop_monitor():
    try:
        monitor.stop_agent_montitor()
    except:
        print >> fp_dlog, '[%s] Failed to stop all agent monitors' % time.strftime(ISOTIMEFMT)
        return False
    return True

def stop_vminfo():
    try:
        vminfo.stop_all()
    except:
        print >> fp_dlog, '[%s] Failed to clean all VM info objects' % time.strftime(ISOTIMEFMT)
        return False
    return True

def start_monitor():
    monitor.start_agent_monitor(vminfo.VMlist)
    return True

def start_daemon():
    vminfo.init_vmlist_from_file()
    vminfo.send_and_start_agent()
    vminfo.start_all()
#    monitor.start_agent_monitor(vminfo.VMlist)
    return True

#def start_monitor():

#vm sys manipulation

def update_vmlist_file(vmlist_lines):
    vmlistfile = get_global('vmlist')
    try:
        fp = open(vmlistfile, 'w')
    except:
        print >> fp_dlog, '[%s] Cannot update vmlist: open file failed' % time.strftime(ISOTIMEFMT)
        print >> fp_dlog, '[%s] Daemon terminated' % time.strftime(ISOTIMEFMT)
        return False
    #update lines
    for line in vmlist_lines:
        #with \n
        fp.write(line)
    fp.close()
    return True

def add_vm(vm):
    """vm here is a dict contains ip, name, uuid, mac, mem_mex, vcpu_max"""
    #start vm agent
    print >> fp_dlog, '[%s] Starting VM agent on %s' %(time.strftime(ISOTIMEFMT), vm.ip)
    cmdline = 'scp -r agent %s:/root' % vm.ip
    print >> fp_dlog, '[%s] %s' %(time.strftime(ISOTIMEFMT), cmdline)
    os.system(cmdline)
    cmdline = 'ssh %s python /root/agent/agent_main.py' % vm.ip
    print >> fp_dlog, '[%s] %s' %(time.strftime(ISOTIMEFMT), cmdline)
    os.system(cmdline)
    #start vminfo and monitor
    vminfo.add_VM(vm)
    monitor.start_agent_monitor_s(vm)
    return True

def del_vm(vmname):
    vminfo.del_VM(vmname)
    monitor.stop_agent_monitor_s(vmname)
    return True

#information retrieve

def get_vm_status():
    vm_status = {}
    for name, vm in vminfo.VMlist.items():
        if vm.status == 0:
            vm_status[name] = 'Stopped'
        elif vm.status == 1:
            vm_status[name] = 'Running'
        elif vm.status == 2:
            vm_status[name] = 'Migrating'
        else:
            vm_status[name] = 'Error/Missing'
    return vm_status

def get_vm_runtime_info():
    vm_rt_info = []
    for name, vm in vminfo.VMlist.items():
        rt_info = {}
        rt_info['name'] = name
        rt_info['ip'] = vm.ip
        rt_info['cpu_rate'] = vm.perfinfo.cpu_rate
        rt_info['mem_ratio'] = vm.perfinfo.mem_ratio
        rt_info['pf_rate'] = vm.perfinfo.pf_rate
        rt_info['diskstat'] = vm.perfinfo.disk_history
        rt_info['netstat'] = vm.perfinfo.net_history
        vm_rt_info.append(rt_info)
    return vm_rt_info


#XMLRPC server
def get_ip_address(ifname='eth0'):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    local_ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])
    return local_ip

class XMLRPC_Server(SimpleXMLRPCServer.SimpleXMLRPCServer):
    allow_reuse_address = True

def start_daemon_server(port=51000, logfilename=''):
    #redirect output
#    logfilename = 'agent-%s.log' % ip
#    fp_log = open(logfilename, 'a+')
#    saveout = sys.stdout
#    saveerr = sys.stderr
#    if not debug:
#        sys.stdour = fp_log
#        sys.stderr = fp_log
    global server
    ip = get_ip_address()
    server = XMLRPC_Server((ip, port))
    server.register_introspection_functions()
    server.register_function(start_daemon, 'start_daemon')
    server.register_function(stop_daemon, 'stop_daemon')
    server.register_function(start_monitor, 'start_monitor')
    server.register_function(stop_monitor, 'stop_monitor')
    server.register_function(stop_vminfo, 'stop_vminfo')
    server.register_function(update_vmlist_file, 'update_vmlist_file')
    server.register_function(add_vm, 'add_vm')
    server.register_function(del_vm, 'del_vm')
    server.register_function(get_vm_status, 'get_vm_status')
    server.register_function(get_vm_runtime_info, 'get_vm_runtime_info')
    server.register_function(daemon_agent.get_perf_info, 'get_perf_info')
    try:
        print >> fp_dlog, 'Starting daemon server...'
        server.serve_forever()
    finally:
	server.server_close()
#        sys.stdout = saveout
#        sys.stderr = saveerr
#        fp_log.close()

def server_init():
    port = get_global('srv_port')
    print port
    start_daemon_server(port)


if __name__ == "__main__":
    print "Hello World";
