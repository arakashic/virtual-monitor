# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Apr 8, 2010 3:56:14 PM$"

import os, sys, time
import fcntl, socket, struct
import SimpleXMLRPCServer

import monitor, nodeinfo
import center_global

ISOTIMEFMT='%Y-%m-%d %X'

def stop_center():
    stop_monitor()
    stop_nodeinfo()
    print >> center_global.fp_clog, '[%s] Stopping daemon' % time.strftime(ISOTIMEFMT)
    server.server_close()
    sys.exit()

def stop_monitor():
    try:
        monitor.stop_daemon_montitor()
    except:
        print >> center_global.fp_clog, '[%s] Failed to stop all daemon monitors' % time.strftime(ISOTIMEFMT)

def stop_nodeinfo():
    try:
        nodeinfo.stop_all()
    except:
        print >> center_global.fp_clog, '[%s] Failed to clean all node info objects' % time.strftime(ISOTIMEFMT)

def start_monitor():
    monitor.start_daemon_monitor(nodeinfo.nodelist)
    return True

def start_center():
    nodeinfo.init_nodelist_from_file()
    nodeinfo.send_and_start_daemon()
    nodeinfo.start_all()
#    monitor.start_daemon_monitor(nodeinfo.nodelist)
    #dispatch vmlists on nodes
    time.sleep(10)
    nodeinfo.init_vmlist_on_node()
    return True

#def start_monitor():

#node sys manipulation

#def update_nodelist_file(nodelist_lines):
#    nodelistfile = center_global.get_global('nodelist')
#    try:
#        fp = open(nodelistfile, 'w')
#    except:
#        print >> center_global.fp_clog, '[%s] Cannot update nodelist: open file failed' % time.strftime(ISOTIMEFMT)
#        print >> center_global.fp_clog, '[%s] Daemon terminated' % time.strftime(ISOTIMEFMT)
#        sys.exit()
#    #update lines
#    for line in nodelist_lines:
#        fp.write(line)
#    fp.close()

def add_node(node):
    """node here is a dict contains ip, name, uuid, mac, mem_mex, cpu_max"""
    #start node daemon
    print >> center_global.fp_clog, '[%s] Starting node daemon on %s' %(time.strftime(ISOTIMEFMT), node.ip)
    cmdline = 'scp -r daemon %s:/root' % node.ip
    print >> center_global.fp_clog, '[%s] %s' %(time.strftime(ISOTIMEFMT), cmdline)
    os.system(cmdline)
    cmdline = 'ssh %s python /root/daemon/daemon_main.py' % node.ip
    print >> center_global.fp_clog, '[%s] %s' %(time.strftime(ISOTIMEFMT), cmdline)
    os.system(cmdline)
    #start nodeinfo and monitor
    nodeinfo.add_node(node)
    monitor.start_daemon_monitor_s(node)

def del_node(nodename):
    nodeinfo.del_node(nodename)
    monitor.stop_daemon_monitor_s(nodename)

#information retrieve

def get_node_status():
    node_status = {}
    for name, node in nodeinfo.nodelist:
        if node.status == 0:
            node_status[name] = 'Stopped'
        elif node.status == 1:
            node_status[name] = 'Running'
        else:
            node_status[name] = 'Error/Missing'
    return node_status

def get_node_runtime_info():
    node_rt_info = []
    for name, node in nodeinfo.nodelist:
        rt_info = {}
        rt_info['name'] = name
        rt_info['ip'] = node.ip
        rt_info['cpu_rate'] = node.perfinfo.cpu_rate
        rt_info['mem_ratio'] = node.perfinfo.mem_ratio
        rt_info['pf_rate'] = node.perfinfo.pf_rate
        rt_info['diskstat'] = node.perfinfo.disk_history
        rt_info['netstat'] = node.perfinfo.net_history
        node_rt_info.append(rt_info)
    return node_rt_info


#XMLRPC server
def get_ip_address(ifname='eth0'):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    local_ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])
    return local_ip

class XMLRPC_Server(SimpleXMLRPCServer.SimpleXMLRPCServer):
    allow_reuse_address = True

def start_center_server(port=8080, logfilename=''):
    #redirect output
#    logfilename = 'daemon-%s.log' % ip
#    fp_log = open(logfilename, 'a+')
#    saveout = sys.stdout
#    saveerr = sys.stderr
#    if not debug:
#        sys.stdour = fp_log
#        sys.stderr = fp_log
    global server
    server = XMLRPC_Server((ip, port))
    server.register_introspection_functions()
    server.register_function(start_center, 'start_center')
    server.register_function(stop_center, 'stop_center')
    server.register_function(start_monitor, 'start_monitor')
    server.register_function(stop_monitor, 'stop_monitor')
    server.register_function(stop_noeinfo, 'stop_nodeinfo')
#    server.register_function(update_vmlist_file, 'update_vmlist_file')
#    server.register_function(add_vm, 'add_vm')
#    server.register_function(del_vm, 'del_vm')
#    server.register_function(get_vm_status, 'get_vm_status')
#    server.register_function(get_vm_runtime_info, 'get_vm_runtime_info')
#    server.register_function(center_agent.get_perf_info, 'get_perf_info')
    try:
        print >> center_global.fp_clog, 'Starting center server...'
        server.serve_forever()
    finally:
	server.server_close()
#        sys.stdout = saveout
#        sys.stderr = saveerr
#        fp_log.close()

def server_init():
    port = center_global.get_global('srv_port')
    start_center_server(port)


if __name__ == "__main__":
    print "Hello World";
