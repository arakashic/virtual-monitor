#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Apr 8, 2010 3:55:56 PM$"

import os, sys, time
import signal

import daemonize
import center_global, comm_service

ISOTIMEFMT='%Y-%m-%d %X'

is_sigint_up = False
def sigint_handler(signum, frame):
    is_sigint_up = True
    stopAll()
    print 'catched interrupt signal!'

def main(argv):
    signal.signal(signal.SIGINT, sigint_handler)
    center_global.global_init()
    comm_service.start_center()
    center_global.cleanup_exit()

if __name__ == "__main__":
    center_global.set_global('is_daemonized', False)
    center_global.set_global('is_monitor', False)
    center_global.set_global('is_daemon_log', False)
    shortopts = 'dlmsp:'
#    longopts = ['hadoop-test-mode', 'start-agent', 'stop-agent', 'test']
    test = '-a -d -m test -m -p'
    try:
        opts, argv = getopt.getopt(sys.argv[1:], shortopts)
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)
    print opts
    print argv
    for o, a in opts:
        if o == '-d':
            center_global.set_global('is_daemonized', True)
        elif o == '-m':
            center_global.set_global('is_monitor', True)
        elif o == '-l':
            center_global.set_global('is_daemon_log', True)

    print center_global.get_global('is_daemonized')
    print center_global.get_global('is_monitor')
    print center_global.get_global('is_daemon_log')
    if center_global.get_global('is_daemonized') == True:
        daemonize.daemonize()
    main(argv)
