# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Apr 21, 2010 11:18:47 AM$"



import nodeinfo
import center_global

ISOTIMEFMT='%Y-%m-%d %X'

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

class NodeResourceAssessor():
    """
    contains a serias of list sorted by different type of free resource
    """
    def __init__(self):
        self.nodelist = nodeinfo.nodelist
        self.node_alive = [node.status == 1 for node in self.nodelist]
        #sorted nodes
        self.list_cpu = [node for node in self.nodelist]
        self.list_mem = [node for node in self.nodelist]
        self.list_iowait = [node for node in self.nodelist]

    def update(self):
        self.list_cpu.sort(\
            lambda x, y: \
                cmp(x.perf_info.avg_cpu_rate(), y.perf_info.avg_cpu_rate()))
        self.list_mem.sort(\
            lambda x, y: \
                cmp((x.perf_info.mem_total - x.perf_info.mem_used),\
                    (y.perf_info.mem_total - y.perf_info.mem_used)))
        self.list_iowait.sort(\
            lambda x, y: \
                cmp(x.perf_info.avg_cpu_iowait_rate(), y.perf_info.avg_cpu_iowait_rate()))

if __name__ == "__main__":
    print "Hello World";
