#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="root"
__date__ ="$Mar 22, 2010 4:18:19 PM$"

import xmlrpclib, sys

if __name__ == "__main__":
    loc = 'http://' + sys.argv[1] + ':' + str(8080)
    srv = xmlrpclib.ServerProxy(loc)
    print srv.get_perf_info()
