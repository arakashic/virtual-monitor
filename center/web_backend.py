# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$May 15, 2010 10:34:37 AM$"

import xmlrpclib

import monitor, nodeinfo
import center_global

ISOTIMEFMT='%Y-%m-%d %X'

def get_centerlog():
    fp = center_global.fp_clog
    fp.flush()
    fp = open(center_global.get_global('logfile'), 'r')
    logs = fp.readlines()
    fp.close()
    return logs

def get_nodelist():
    ret = []
    for name, node in nodeinfo.nodelist.items():
        data = {}
        data['name'] = name
        data['ip'] = node.ip
        data['mac'] = node.mac
        data['mem'] = node.mem_max
        data['cpu'] = node.cpu_max
        data['status'] = nodeinfo.status_str[node.status]

        loc = 'http://%s:%d' % (node.ip, node.port)
        srv = xmlrpclib.ServerProxy(loc)
        try:
            vmlist = srv.get_vmlist()
            data['vmlist'] = vmlist
        except:
            pass
#        print data
        ret.append(data)

    return ret

if __name__ == "__main__":
    print "Hello World";
