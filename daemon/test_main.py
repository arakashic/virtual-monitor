#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="root"
__date__ ="$Mar 22, 2010 4:18:19 PM$"

import getopt
import xmlrpclib, sys

if __name__ == "__main__":
    loc = 'http://' + sys.argv[1] + ':' + str(51000)
    srv = xmlrpclib.ServerProxy(loc)
    lists = ['a\n', 'b\n', 'c\n']
#    srv.update_vmlist_file(lists)
    srv.start_daemon()
    srv.stop_daemon()

#    shortopts = 'admsp:'
#    longopts = ['hadoop-test-mode', 'start-agent', 'stop-agent', 'test']
#    test = '-adm abc test2'.split()
#    try:
#        opts, argv = getopt.getopt(test, shortopts, [])
#    except getopt.GetoptError, err:
#        print str(err)
#        sys.exit(2)
#    print opts
#    print argv
#
