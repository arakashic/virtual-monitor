# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Apr 21, 2010 11:18:47 AM$"

import sys, time

import nodeinfo
import center_global

ISOTIMEFMT='%Y-%m-%d %X'

fp_reslog = center_global.fp_clog

class NodeResourceScore():
    """
    contains resource score of each type (eg. cpu, mem)
    """
    def __init__(self, node):
        self.node = node
        #score of each resource type
        self.score_cpu = 0
        self.score_mem = 0
        self.score_iowait = 0

    def get_overall_score(self):
        score_overall = self.score_cpu + self.score_mem + self.score_iowait
        return score_overall

    def output(self):
        print '%s %d %d %d' % (self.node.name, self.score_cpu, self.score_mem, self.score_iowait)

class NodeResourceAssessor():
    """
    contains a serias of list sorted by different type of free resource
    """
    def __init__(self):
        self.nodelist = nodeinfo.nodelist
        self.node_alive = [node.status == 1 for name, node in self.nodelist.items()]
        #sorted nodes
        self.list_cpu = [node for name, node in self.nodelist.items()]
        self.list_mem = [node for name, node in self.nodelist.items()]
        self.list_iowait = [node for name, node in self.nodelist.items()]
        #node res score dict
        self.res_scores = {}
        for name, node in nodeinfo.nodelist.items():
            res_score = NodeResourceScore(node)
            self.res_scores[name] = res_score


    def update(self):
        self.list_cpu.sort(\
            lambda x, y: \
                cmp(x.perf_info.avg_cpu_rate(), y.perf_info.avg_cpu_rate()))
        i = 0
        for node in self.list_cpu:
            i += 1
            self.res_scores[node.name].score_cpu = i
        self.list_mem.sort(\
            lambda x, y: \
                cmp((x.perf_info.mem_total - x.perf_info.mem_used),\
                    (y.perf_info.mem_total - y.perf_info.mem_used)))
        i = 0
        for node in self.list_mem:
            i += 1
            self.res_scores[node.name].score_mem = i
        #iowait less first
        self.list_iowait.sort(\
            lambda x, y: \
                cmp(x.perf_info.avg_cpu_iowait_rate(), y.perf_info.avg_cpu_iowait_rate()))
        #refresh node scores
        i = 0
        for node in self.list_iowait:
            i += 1
            self.res_scores[node.name].score_iowait = i
        return True

    def get_max_free_cpu(self):
        return (self.list_cpu[0].ip, self.list_cpu[0].port)

    def get_max_free_mem(self):
        return (self.list_mem[0].ip, self.list_mem[0].port)

    def get_max_free_io(self):
        return (self.list_iowait[0].ip, self.list_iowait[0].port)

    def get_most_avaliable_node(self):
        t = 0
        nodename = ''
        for name, res_score in self.res_scores.items():
            s = res_score.get_overall_score()
            if t < s:
                t = s
                nodename = name
        node = self.res_scores[nodename].node
        return (node.ip, node.port)

    def output(self):
        print >> fp_reslog, center_global.syb_sep
        print >> fp_reslog, '[%s] Resource lists:' % time.strftime(ISOTIMEFMT)
        print >> fp_reslog, '\tCPU: %s' % str(self.list_cpu)
        print >> fp_reslog, '\tMEM: %s' % str(self.list_mem)
        print >> fp_reslog, '\tIOWAIT: %s' % str(self.list_iowait)
        for name, res_score in self.res_scores.items():
            res_score.output()
#        print >> fp_reslog, center_global.syb_sep

if __name__ == "__main__":
    print "Hello World";
