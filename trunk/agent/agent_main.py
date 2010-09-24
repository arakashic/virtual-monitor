#! /usr/bin/python
# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Mar 22, 2010 3:23:54 PM$"

import os, sys
import SimpleXMLRPCServer
import socket, struct, fcntl

import re

from time import mktime, localtime
from iostat.netstat import read_netstat
from iostat.diskstat import read_diskstat

from daemonize import daemonize

#debug=0
#port=8080

class XMLRPC_Server(SimpleXMLRPCServer.SimpleXMLRPCServer):
    allow_reuse_address = True

#agent service

def heart_beat():
    return True
    
def get_perf_info():
    """time stamp is inn ctime
    cpu readings returns in total and idle count
    mem size returns in total and used size KBs
    page fault rate returns in current accumulated total pf reading
    diskstat and netstat returns in overall accumulated readings
    to finally use these data, you need calculate the delta of pf, disk and net"""
    #read in all info
    fp_intr = open('/proc/vmstat', 'r')
    intr_lines = fp_intr.readlines()
    fp_intr.close()
    fp_mem = open('/proc/meminfo', 'r')
    mem_line = fp_mem.read()
    fp_mem.close()
    fp_cpu = open('/proc/stat', 'r')
    cpu_lines = fp_cpu.readlines()
    fp_cpu.close()
    #get cpu readings
    cpu_data = cpu_lines[0].split(' ')
    cpu_total = 0
    cpu_idle = float(cpu_data[5])
    cpu_iowait = float(cpu_data[6])
    for i in range(2, 10):
        cpu_total += float(cpu_data[i])
    #get current mem usage
    MemTotal = float(mem_line[mem_line.find('MemTotal:') + 9: mem_line.find(' kB')].strip())
    MemFree = float(mem_line[mem_line.find('MemFree:') + 8: mem_line.find(' kB', mem_line.find('MemFree:'))].strip())
    Buffers = float(mem_line[mem_line.find('Buffers:') + 8: mem_line.find(' kB', mem_line.find('Buffers:'))].strip())
    Cached  = float(mem_line[mem_line.find('Cached:') + 7: mem_line.find(' kB', mem_line.find('Cached:'))].strip())
    MemUsed = MemTotal - MemFree - Buffers - Cached
    #pagefault
    for line in intr_lines:
        if re.search(r'^pgfault', line):
            page_intr = int(line.split(' ')[1].strip())
            continue
        if re.search(r'^pgmajfault', line):
            page_maj_intr = int(line.split(' ')[1].strip())
            continue
    page_intr -= page_maj_intr
    #get disk and net stat
    diskstat = read_diskstat()
    netstat = read_netstat()
    #get time stamp
    timestamp = mktime(localtime())
    #put in output dict
    result = {'time':timestamp,\
              'cpu_total':cpu_total,\
              'cpu_idle':cpu_idle,\
              'cpu_iowait':cpu_iowait,\
              'mem_total':MemTotal,\
              'mem_used':MemUsed,\
              'pagefault':page_intr,\
              'diskstat':diskstat[0],\
              'netstat':netstat[0]}

    return result

def stop_agent():
    server.server_close()
    os._exit(0)
    return None

#end agent service

def get_ip_address(ifname='eth0'):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    local_ip = socket.inet_ntoa(\
        fcntl.ioctl(s.fileno(), 0x8915,\
            struct.pack('256s', ifname[:15]))[20:24])
    return local_ip

def read_config(filename='agent.conf'):
    global port
    global ip
    global debug
    debug = 0
    fp_cfg = open(filename, 'r')
    cfg_lines = fp_cfg.readlines()
    fp_cfg.close()
    for line in cfg_lines:
        if re.search(r'^PORT', line):
            port = int(line.split('=')[1].strip())
            continue
        if re.search(r'^DEBUG', line):
            debug = int(line.split('=')[1].strip())
            continue
    ip= get_ip_address()

def start_agent(port=8080, logfilename=''):
    #redirect output
    logfilename = 'agent-%s.log' % ip
    fp_log = open(logfilename, 'a+')
    saveout = sys.stdout
    saveerr = sys.stderr
    if not debug:
        sys.stdour = fp_log
        sys.stderr = fp_log
    global server
    server = XMLRPC_Server((ip, port))
    server.register_introspection_functions()
    server.register_function(get_perf_info, 'get_perf_info')
    server.register_function(stop_agent, 'stop_agent')
    server.register_function(heart_beat, 'heart_beat')
    try:
        print 'Starting server......'
        server.serve_forever()
    finally:
	server.server_close()
        sys.stdout = saveout
        sys.stderr = saveerr
        fp_log.close()
        

def main():
    cwd = os.path.abspath(__file__)
    cwd = os.path.dirname(cwd)
#    print cwd
    os.chdir(cwd)
    read_config()
#    global ip
#    ip = get_ip_address()
    start_agent()

if __name__ == "__main__":
    daemonize()
    main()
