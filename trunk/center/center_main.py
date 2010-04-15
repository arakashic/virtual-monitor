#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Apr 8, 2010 3:55:56 PM$"

import os, sys, time
import signal

import center_global, comm_service

ISOTIMEFMT='%Y-%m-%d %X'

is_sigint_up = False
def sigint_handler(signum, frame):
    is_sigint_up = True
    stopAll()
    print 'catched interrupt signal!'

if __name__ == "__main__":
#    print "Hello World";
    signal.signal(signal.SIGINT, sigint_handler)
    center_global.global_init()
    comm_service.start_center()
