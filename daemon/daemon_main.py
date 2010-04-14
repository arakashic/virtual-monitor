#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Mar 22, 2010 9:25:15 PM$"

import os, sys, time, getopt
import thread, signal

import daemonize

import monitor
import daemon_global
import vminfo
from comm_service import server_init
#import daemon_control

ISOTIMEFMT='%Y-%m-%d %X'

is_sigint_up = False
def sigint_handler(signum, frame):
    is_sigint_up = True
    daemon_global.cleanup_exit()
    print >> daemon_global.fp_dlog, 'catched interrupt signal!'

def main():
    signal.signal(signal.SIGINT, sigint_handler)
#    daemon_global.start_daemon_log()
    if len(sys.argv) <= 1:
#        vminfo.init_vmlist_from_file()
#        vminfo.start_all()
#        monitor.start_agent_monitor(vminfo.VMlist)
#        print monitor.threadlist
#        time.sleep(1000)
        sys.exit()
    daemon_global.global_init()
    if sys.argv[1] == 'start_agent':
        vminfo.init_vmlist_from_file()
        vminfo.send_and_start_agent()
    if sys.argv[1] == 'stop_agent':
        vminfo.init_vmlist_from_file()
        for name, vm in vminfo.VMlist.items():
            vm.stop()
    if sys.argv[1] == 'start_mon':
        vminfo.init_vmlist_from_file()
        vminfo.start_all()
        monitor.start_agent_monitor(vminfo.VMlist)
        print >> daemon_global.fp_dlog, 'Test System Ready, GO!!!'
        print >> daemon_global.fp_dlog, '0 load test for 600 sec'
#        print monitor.threadlist
        time.sleep(6000)
    if sys.argv[1] == 'start_mon_adj':
        vminfo.init_vmlist_from_file()
        vminfo.start_all()
        monitor.start_agent_monitor(vminfo.VMlist)
        print >> daemon_global.fp_dlog, 'Test System Ready, GO!!!'
        print >> daemon_global.fp_dlog, '0 load test for 600 sec'
        monitor.start_adjust_thread()
#        print monitor.threadlist
        time.sleep(6000)
    if sys.argv[1] == 'hadoop_test_mode':
        print >> daemon_global.fp_dlog, 'Hadoop Test Mode'
        vminfo.init_vmlist_from_file()
        vminfo.start_all()
        monitor.start_agent_monitor(vminfo.VMlist)
        time.sleep(5)
        print >> daemon_global.fp_dlog, 'Test System Ready, GO!!!'
        time.sleep(5)
        cmdline = 'ssh 127.0.0.1 /root/hadoop/hadoop/bin/hadoop jar \
                   /root/hadoop/hadoop/hadoop-0.20.2-examples.jar \
                   wordcount testin_data3 testout_data3_4'
        print cmdline
        os.system(cmdline)
        time.sleep(10)
        print >> daemon_global.fp_dlog, 'Test end'
#        vminfo.del_VM('cloud1')
    if sys.argv[1] == 'test':
        print >> daemon_global.fp_dlog, 'test mode'
        time.sleep(60)
    if sys.argv[1] == 'server':
#        vminfo.init_vmlist_from_file()
#        vminfo.start_all()
#        monitor.start_agent_monitor(vminfo.VMlist)
#        print >> daemon_global.fp_dlog, 'Test System Ready, GO!!!'
#        print >> daemon_global.fp_dlog, '0 load test for 600 sec'
        thread.start_new_thread(server_init,())
        time.sleep(1000)

    daemon_global.cleanup_exit()
        
if __name__ == "__main__":
#    DAEMONIZE = False
#    START_AGENT = False
#    STOP_AGENT = False
#    MONITOR = False
#    ADJUST = False
#    SERVER = False
#    HADOOP_TEST = False
#    TEST = False
    daemon_global.set_global('is_daemonized', False)
    daemon_global.set_global('is_adjust', False)
    daemon_global.set_global('is_monitor', False)
#    if len(sys.argv) == 3 and sys.argv[2] == 'daemon':
#        daemonize.daemonize()
#    main()
    shortopts = 'admsp:'
    longopts = ['hadoop-test-mode', 'start-agent', 'stop-agent', 'test']
    test = '-a -d -m test -m -p'
    try:
        opts, argv = getopt.getopt(test, shortopts)
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)
    for o, a in opts:
        if o == 'd':
            daemon_global.set_global('is_daemonized', True)
        elif o == 'a':
            daemon_global.set_global('is_adjust', True)
        elif o == 'm':
            daemon_global.set_global('is_monitor', True)
#    if daemon_global.get_global('is_daemonized') == True:
#        daemonize.daemonize()
#    main()
