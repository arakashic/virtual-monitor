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
                'nodelist':'nodelist.lst'}

fp_clog = sys.stdout
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

def get_ip_address(ifname='eth0'):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    local_ip = socket.inet_ntoa(\
        fcntl.ioctl(s.fileno(), 0x8915,\
            struct.pack('256s', ifname[:15]))[20:24])
    return local_ip

def read_center_config(filename='center.conf'):
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
        if re.search(r'^NODELIST', line):
            param_global['nodelist'] = line.split('=')[1].strip()
            continue
        if re.search(r'^SRV_PORT', line):
            param_global['srv_port'] = int(line.split('=')[1].strip())
            continue
        if re.search(r'^LOGFILE', line):
            param_global['logfile'] = line.split('=')[1].strip()
            continue
        if re.search(r'^VM-NODELIST', line):
            param_global['vm-nodelist'] = line.split('=')[1].strip()
            continue

def start_center_log():
    global fp_clog
    CENTER_LOG = get_global('is_center_log')
    if CENTER_LOG:
#        print 'open log'
        logfile = param_global['logfile']
        fp_clog = open(logfile, 'a+')
    else:
        fp_clog = sys.stdout
    

def stop_center_log():
    global fp_clog
    if fp_clog == sys.stdout:
        pass
    else:
        fp_clog.close()

def global_init():
    cwd = os.path.abspath(__file__)
    cwd = os.path.dirname(cwd)
    param_global['cwd'] = cwd
    os.chdir(cwd)
    read_center_config()
    
    start_center_log()
    print >> fp_clog, '[%s] =======<<Center Started>>===========================' % time.strftime(ISOTIMEFMT)
    print >> fp_clog, param_global
#    try:
#        param_global['pm_ip'] = get_ip_address()
#    except:
#        print 'Exception when getting PM ip'
    
    data_path = os.path.join(cwd, param_global['data_dir'])
    try:
        os.mkdir(data_path)
    except:
        pass


def cleanup_exit():
    print >> fp_clog, '[%s] =======<<Center Exited>>============================' % time.strftime(ISOTIMEFMT)
    stop_center_log()
    print 'exit'
    os._exit(0)


if __name__ == "__main__":
    print "Hello World";
    global_init()
    print param_global
