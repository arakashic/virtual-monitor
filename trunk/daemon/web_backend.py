# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$May 11, 2010 2:15:28 PM$"

import os, sys, time
import fcntl, socket, struct
import SimpleXMLRPCServer

import monitor, vminfo, daemon_agent
import daemon_global

ISOTIMEFMT='%Y-%m-%d %X'

#web service service
def get_daemonlog():
    fp = daemon_global.fp_dlog
    fp.flush()
    fp = open(daemon_global.get_global('logfile'), 'r')
    logs = fp.readlines()
    fp.close()
    return logs

def get_vmlist():
    ret = []
    for name, vm in vminfo.VMlist.items():
        data = {}
        data['name'] = name
        data['ip'] = vm.ip
        data['uuid'] = vm.uuid
        data['mac'] = vm.mac
        data['mem'] = vm.mem_max
        data['vcpu'] = vm.vcpu_max
        data['status'] = vminfo.status_str[vm.status]
#        print data
        ret.append(data)

    return ret

def get_vmperflist():
    ret = []
    for name, vm in vminfo.VMlist.items():
        data = {}
        data['name'] = name
        data['cpu'] = vm.perf_info.cpu_rate
        data['cpu_avg'] = vm.perf_info.avg_cpu_rate()
        data['iowait'] = vm.perf_info.cpu_iowait_rate
        data['iowait_avg'] = vm.perf_info.avg_cpu_iowait_rate()
        data['mem'] = vm.perf_info.mem_ratio
        data['mem_avg'] = vm.perf_info.avg_mem_ratio()
        data['pf'] = vm.perf_info.pf_rate
        data['pf_avg'] = vm.perf_info.avg_pf_rate()
        data['diskrd'] = vm.perf_info.disk_read
        data['diskwr'] = vm.perf_info.disk_write
        data['netsend'] = vm.perf_info.net_trans
        data['netrecv'] = vm.perf_info.net_recv
#        print data
        ret.append(data)

    return ret

#class XMLRPC_Server(SimpleXMLRPCServer.SimpleXMLRPCServer):
#    allow_reuse_address = True
#
#def start_daemon_server(port=51000, logfilename=''):
#    #redirect output
##    logfilename = 'agent-%s.log' % ip
##    fp_log = open(logfilename, 'a+')
##    saveout = sys.stdout
##    saveerr = sys.stderr
##    if not debug:
##        sys.stdour = fp_log
##        sys.stderr = fp_log
#    global server
#    ip = get_ip_address()
#    daemon_global.set_global('pm_ip', ip)
#    server = XMLRPC_Server((ip, port))
#    server.register_introspection_functions()
#    server.register_function(start_daemon, 'start_daemon')
#    server.register_function(stop_daemon, 'stop_daemon')
#    server.register_function(start_monitor, 'start_monitor')
#    server.register_function(stop_monitor, 'stop_monitor')
#    server.register_function(stop_vminfo, 'stop_vminfo')
#    server.register_function(update_vmlist_file, 'update_vmlist_file')
#    server.register_function(start_new_vm, 'start_new_vm')
##    server.register_function(del_vm, 'del_vm')
#    server.register_function(get_vm_status, 'get_vm_status')
#    server.register_function(get_vm_runtime_info, 'get_vm_runtime_info')
#    server.register_function(daemon_agent.get_perf_info, 'get_perf_info')
#    server.register_function(center_sign, 'center_sign')
#    server.register_function(center_unsign, 'center_unsign')
#    try:
#        print >> daemon_global.fp_dlog, 'Starting daemon server...'
#        server.serve_forever()
#    finally:
#	server.server_close()
##        sys.stdout = saveout
##        sys.stderr = saveerr
##        fp_log.close()
#
#def server_init():
#    port = daemon_global.get_global('srv_port')
#    print port
#    start_daemon_server(port)


if __name__ == "__main__":
    print "Hello World";
