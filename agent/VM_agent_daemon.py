#! /usr/bin/python
# author : AFu
# edit   :Harry

import fcntl
import struct
import time

import SimpleXMLRPCServer
import os
import socket

import sys, time
#from iostat.diskstat import read_diskstat
#from iostat.netstat import read_netstat

#netstat
def read_netstat(path = '/proc/net/dev'):
    netstat_by_interface = list()
    netstat_overall = { 'if_name':'overall', 'recv_bytes':0,
                'recv_packets':0, 'recv_drop':0, 'recv_fifo':0, 'recv_frame':0,
                'recv_compressed':0, 'multicast':0, 'trans_bytes':0,
                'trans_packets':0, 'trans_drop':0, 'trans_fifo':0,
                'trans_frame':0, 'trans_compressed':0 }

    dev = file(path,'r')

    lines = dev.readlines()

    for count in range(2, len(lines)-1):

        line = lines[count].split()
        dev_info = {'if_name' : line[0],
                'recv_bytes' : int(line[1]), 'recv_packets' : int(line[2]),
                'recv_drop' : int(line[3]), 'recv_fifo' : int(line[4]),
                'recv_frame' : int(line[5]), 'recv_compressed' : int(line[6]),
                'multicast' : int(line[7]), 'trans_bytes' : int(line[8]),
                'trans_packets' : int(line[9]), 'trans_drop' : int(line[10]),
                'trans_fifo' : int(line[11]), 'trans_frame' : int(line[12]),
                'trans_compressed' : int(line[13]) }
        netstat_by_interface.append(dev_info)
        for key in netstat_overall.keys():
            if not key == 'if_name':
                netstat_overall[key] += dev_info[key]
    dev.close()
    return (netstat_overall, netstat_by_interface)

#diskstat
def read_diskstat(path = '/proc/diskstats'):
    diskstat_by_label = list()
    diskstat_overall = { 'major':0, 'minor':0, 'label':'overall',
                'reads_completed':0, 'reads_merged':0,
                'sectors_read':0, 'milliseconds_reading':0,
                'writes_completed':0,'writes_merged':0,
                'sectors_written':0, 'milliseconds_writing':0,
                'ios_in_progress':0, 'milliseconds_io':0,
                'weighted_milliseconds_io':0 }

    disks = file(path,'r')

    lines = disks.readlines()

    for count in range(0, len(lines)-1):

        line = lines[count].split()
        disk_info = {'major' : int(line[0]), 'minor' : int(line[1]),
                    'label' : line[2],
                    'reads_completed' : int(line[3]),
                    'reads_merged':int(line[4]),
                    'sectors_read' : int(line[5]),
                    'milliseconds_reading' : int(line[6]),
                    'writes_completed' : int(line[7]),
                    'writes_merged':int(line[8]), 'sectors_written' : int(line[9]),
                    'milliseconds_writing' : int(line[10]),
                    'ios_in_progress' :int(line[11]),
                    'milliseconds_io' : int(line[12]),
                    'weighted_milliseconds_io' : int(line[13]) }
        diskstat_by_label.append(disk_info)
        for key in diskstat_overall.keys():
            if not key in ['label','major','minor']:
                diskstat_overall[key] += disk_info[key]
    disks.close()
    return (diskstat_overall, diskstat_by_label)

def daemonize(stdout='/dev/null', stderr=None, stdin='/dev/null',
              pidfile=None, startmsg='started with pid %s'):
    '''
        This forks the current process into a daemon.
        The stdin, stdout, and stderr arguments are file names that
        will be opened and be used to replace the standard file descriptors
        in sys.stdin, sys.stdout, and sys.stderr.
        These arguments are optional and default to /dev/null.
        Note that stderr is opened unbuffered, so
        if it shares a file with stdout then interleaved output
        may not appear in the order that you expect.
    '''
    # Do first fork.
    try:
        pid = os.fork()
        if pid > 0: sys.exit(0) # Exit first parent.
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)

    # Decouple from parent environment.
    os.chdir("/")
    os.umask(0)
    os.setsid()

    # Do second fork.
    try:
        pid = os.fork()
        if pid > 0: sys.exit(0) # Exit second parent.
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)

    # Open file descriptors and print start message
    if not stderr: stderr = stdout
    si = file(stdin, 'r')
    so = file(stdout, 'a+')
    se = file(stderr, 'a+', 0)
    pid = str(os.getpid())
    sys.stderr.write("\n%s\n" % startmsg % pid)
    sys.stderr.flush()
    if pidfile: file(pidfile, 'w+').write("%s\n" % pid)

    # Redirect standard file descriptors.
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def get_ip_address(ifname='eth0'):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    local_ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])
    return local_ip


def getPerfInfo():
    fp_intr = open('/proc/vmstat', 'r')
    intr = fp_intr.read()
    fp_intr.close()
    tmp = intr[intr.find('pgfault'):]
    page_intr = int(tmp[tmp.find(' ') + 1:tmp.find('\n')])
    tmp = intr[intr.find('pgmajfault'):]
    page_maj_intr = int(tmp[tmp.find(' ') + 1:tmp.find('\n')])
    page_intr -= page_maj_intr
###############################################################
    fp_mem = open('/proc/meminfo', 'r')
    meminfo = fp_mem.read()
    fp_mem.close()
    MemTotal = float(meminfo[meminfo.find('MemTotal:') + 9: meminfo.find(' kB')].strip())
    MemFree = float(meminfo[meminfo.find('MemFree:') + 8: meminfo.find(' kB', meminfo.find('MemFree:'))].strip())
    Buffers = float(meminfo[meminfo.find('Buffers:') + 8: meminfo.find(' kB', meminfo.find('Buffers:'))].strip())
    Cached  = float(meminfo[meminfo.find('Cached:') + 7: meminfo.find(' kB', meminfo.find('Cached:'))].strip())
    MemRatio = (MemTotal - MemFree - Buffers - Cached) / MemTotal * 100
###############################################################
    fp_cpu = open('/proc/stat', 'r')
    cpu_lines = fp_cpu.readlines()
    cpu_data = cpu_lines[0].split(' ')
    cpu_total = 0
    cpu_idle = float(cpu_data[5])
    for i in range(2, 10):
        cpu_total += float(cpu_data[i])
###############################################################
    disk_stat = read_diskstat()
    net_stat = read_netstat()
###############################################################
    now = time.strftime('%Y-%m-%d %X')
    result = {'t': now,
    'm': MemRatio,
    'p': page_intr,
    'cpu_idle': cpu_idle,
    'cpu_total': cpu_total,
    'diskio': disk_stat[0],
    'netio': net_stat[0]}
###############################################################
    return result

def getTotalMem():
    fp_mem = open('/proc/meminfo', 'r')
    meminfo = fp_mem.read()
    fp_mem.close()
    MemTotal = float(meminfo[meminfo.find('MemTotal:') + 9: meminfo.find(' kB')].strip())
    MemTotal = MemTotal / 1024
    return int(MemTotal)

def stop_server():
    server.server_close()
    os._exit(0)
    return None

def selfTest():
    return 1

class XMLRPC_Server(SimpleXMLRPCServer.SimpleXMLRPCServer):
    allow_reuse_address = True

def main():
    global server
    server = XMLRPC_Server((get_ip_address(), 8080))
    server.register_function(getPerfInfo, 'getPerfInfo')
    server.register_function(stop_server, 'stopAgent')
    server.register_function(selfTest, 'SelfTest')
    server.register_function(getTotalMem, 'GetTotalMem')
    try:
        server.serve_forever()
    finally:
	server.server_close()

if __name__ == '__main__':
    daemonize()
    main()
#    print str(getPerfInfo())


