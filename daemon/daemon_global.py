# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei"
__date__ ="$Mar 22, 2010 5:32:37 PM$"

import os, sys, time
import re
import socket, struct, fcntl

ISOTIMEFMT='%Y-%m-%d %X'

param_global = {'debug':0,\
                'data_dir':'data',\
                'vmlist':'vmlist.lst'}

#daemon log file
fp_dlog = sys.stdout
syb_sep = '------------------------------------------------------------'

def get_global(key):
    if param_global.has_key(key):
        return param_global[key]
    else:
        return None

def set_global(key, value):
    param_global[key] = value

def del_global(key):
    if param_global.has_key(key):
        del param_global[key]
        return True
    else:
        return False

#def get_ip_address(ifname='eth0'):
#    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#    local_ip = socket.inet_ntoa(\
#        fcntl.ioctl(s.fileno(), 0x8915,\
#            struct.pack('256s', ifname[:15]))[20:24])
#    return local_ip

def read_daemon_config(filename='daemon.conf'):
    fp = open(filename, 'r')
    filelines = fp.readlines()
    fp.close()
    for line in filelines:
        if re.search(r'^DEBUG', line):
            param_global['debug'] = int(line.split('=')[1].strip())
            continue
        if re.search(r'^DATA_DIR', line):
            param_global['data_dir'] = line.split('=')[1].strip()
            continue
        if re.search(r'^VMLIST', line):
            param_global['vmlist'] = line.split('=')[1].strip()
            continue
        if re.search(r'^SRV_PORT', line):
            param_global['srv_port'] = int(line.split('=')[1].strip())
            continue
        if re.search(r'^LOGFILE', line):
            param_global['logfile'] = line.split('=')[1].strip()
            continue

def start_daemon_log():
    global fp_dlog
#    from daemon_global import fp_dlog
    DAEMON_LOG = get_global('is_daemon_log')
    if DAEMON_LOG == True:
        print 'open log'
        logfile = param_global['logfile']
        fp_dlog = open(logfile, 'a+')
    else:
        fp_dlog = sys.stdout


def stop_daemon_log():
    global fp_dlog
#    from daemon_global import fp_dlog
    if fp_dlog == sys.stdout:
        pass
    else:
        fp_dlog.close()

def global_init():
    cwd = os.path.abspath(__file__)
    cwd = os.path.dirname(cwd)
    param_global['cwd'] = cwd
    os.chdir(cwd)
    read_daemon_config()
    
    start_daemon_log()
    print >> fp_dlog, '[%s] =======<<Daemon Started>>===========================' % time.strftime(ISOTIMEFMT)
    print >> fp_dlog, param_global
#    print >> fp_dlog, 'test'
#    try:
#        param_global['pm_ip'] = get_ip_address()
#    except:
#        print >> fp_dlog, 'Exception when getting PM ip'
    
    data_path = os.path.join(cwd, param_global['data_dir'])
    try:
        os.mkdir(data_path)
    except:
        pass

def cleanup_exit():
    print >> fp_dlog, '[%s] =======<<Daemon Exited>>============================' % time.strftime(ISOTIMEFMT)
    stop_daemon_log()
    print 'exit'
    os._exit(0)


if __name__ == "__main__":
    print "Hello World";
    global_init()
    print param_global
