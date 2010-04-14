#!/usr/bin/env python

import sys
from time import sleep

def read_diskstat(path = '/proc/diskstats'):
    diskstat_by_label = list()
    diskstat_overall = { 'major':0, 'minor':0, 'label':'overall',
                'reads_completed':0, 'reads_merged':0,
                'sectors_read':0, 'milliseconds_reading':0,
                'writes_completed':0,'writes_merged':0,
                'sectors_written':0, 'milliseconds_writing':0,
                'ios_in_progress':0, 'milliseconds_io':0,
                'weighted_milliseconds_io':0 }
    
    disks = file(path,'r')
    
    lines = disks.readlines()
    
    for count in range(0, len(lines)-1):
        
        line = lines[count].split()   
        disk_info = {'major' : int(line[0]), 'minor' : int(line[1]),
                    'label' : line[2],
                    'reads_completed' : int(line[3]),
                    'reads_merged':int(line[4]),
                    'sectors_read' : int(line[5]),
                    'milliseconds_reading' : int(line[6]),
                    'writes_completed' : int(line[7]),
                    'writes_merged':int(line[8]), 'sectors_written' : int(line[9]),
                    'milliseconds_writing' : int(line[10]),
                    'ios_in_progress' :int(line[11]),
                    'milliseconds_io' : int(line[12]),
                    'weighted_milliseconds_io' : int(line[13]) }
        diskstat_by_label.append(disk_info)
        for key in diskstat_overall.keys():
            if not key in ['label','major','minor']:
                diskstat_overall[key] += disk_info[key]
    disks.close()
    return (diskstat_overall, diskstat_by_label)

def diskstat(prev, current, interval):
    prev_overall = prev[0]
    current_overall = current[0]
    stat = { 'label' : 'overall',
             'read_throughput' : float(current_overall['sectors_read']-prev_overall['sectors_read'])/interval*512,
             'write_throughput' : float(current_overall['sectors_written']-prev_overall['sectors_written'])/interval*512,
             'read_rate' : float(current_overall['reads_completed']-prev_overall['reads_completed'])/interval,
             'write_rate' : float(current_overall['writes_completed']-prev_overall['writes_completed'])/interval,
             'reads_completed' : current_overall['reads_completed'],
             'writes_completed' : current_overall['writes_completed'],
             'data_read' : current_overall['sectors_read']*512,
             'data_write': current_overall['sectors_written']*512 }
    return stat


    

if __name__ == "__main__":
    while 0 != 1:
        a=read_diskstat()
        sleep(1)
        b=read_diskstat()
        print diskstat(a,b,1)

    
