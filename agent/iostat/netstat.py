#!/usr/bin/env python

import sys
from time import sleep

def read_netstat(path = '/proc/net/dev'):
    netstat_by_interface = list()
    netstat_overall = { 'if_name':'overall', 'recv_bytes':0,
                'recv_packets':0, 'recv_drop':0, 'recv_fifo':0, 'recv_frame':0,
                'recv_compressed':0, 'multicast':0, 'trans_bytes':0,
                'trans_packets':0, 'trans_drop':0, 'trans_fifo':0,
                'trans_frame':0, 'trans_compressed':0 }
    
    dev = file(path,'r')
    
    lines = dev.readlines()
    
    for count in range(2, len(lines)-1):
        
        line = lines[count].split()   
        dev_info = {'if_name' : line[0],
                'recv_bytes' : int(line[1]), 'recv_packets' : int(line[2]),
                'recv_drop' : int(line[3]), 'recv_fifo' : int(line[4]),
                'recv_frame' : int(line[5]), 'recv_compressed' : int(line[6]),
                'multicast' : int(line[7]), 'trans_bytes' : int(line[8]),
                'trans_packets' : int(line[9]), 'trans_drop' : int(line[10]),
                'trans_fifo' : int(line[11]), 'trans_frame' : int(line[12]),
                'trans_compressed' : int(line[13]) }
        netstat_by_interface.append(dev_info)
        for key in netstat_overall.keys():
            if not key == 'if_name':
                netstat_overall[key] += dev_info[key]
    dev.close()
    return (netstat_overall, netstat_by_interface)

def netstat(prev, current, interval):
    prev_overall = prev[0]
    current_overall = current[0]
    stat = { 'interface_name' : 'overall',
             'receive_throughput' : float(current_overall['recv_bytes'] - prev_overall['recv_bytes'])/interval,
             'transmit_throughput' : float(current_overall['trans_bytes'] - prev_overall['trans_bytes'])/interval,
             'receive_packet_rate' : float(current_overall['recv_packets'] - prev_overall['recv_packets'])/interval,
             'transmit_packet_rate' : float(current_overall['trans_packets'] -prev_overall['trans_packets'])/interval,
             'packets_received' : current_overall['recv_packets'],
             'packets_transmitted' : current_overall['trans_packets'],
             'data_received' : current_overall['recv_bytes'],
             'data_transmitted': current_overall['trans_bytes'] }
    return stat

if __name__ == "__main__":
    a=read_netstat()
    sleep(1)
    b=read_netstat()
    print netstat(a,b,1)

    
