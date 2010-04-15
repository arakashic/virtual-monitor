#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Mar 25, 2010 2:42:12 PM$"

import os, sys, time
import re

ISOTIMEFMT='%Y-%m-%d %X'

#print switch
#all labels
PRINT_LABEL=True
#sub time, finish time, etc
PRINT_BASIC=False
#info of each task
PRINT_TASK_LIST=True
#finished/failed maps/reduces, rack/data-local maps, etc
PRINT_SUMMARY=False

def parse_hadoop_job_title(lines):
    for line in lines:
        res = re.search(r'SUBMIT_TIME="\d+"', line)
        if res:
#            print res.group()
            hadoop_info['submit_time'] = int(re.search(r'\d+', res.group()).group())
            continue
        res = re.search(r'Job JOBID="\w+" FINISH_TIME="\d+"', line)
        if res:
            hadoop_info['finish_time'] = int(re.search(r'\d{13}', res.group()).group())
            continue
        res = re.search(r'Job JOBID="\w+" LAUNCH_TIME="\d+"', line)
        if res:
            hadoop_info['launch_time'] = int(re.search(r'\d{13}', res.group()).group())
            continue

def parse_task_info(lines):
    for line in lines:
        res = re.search(r'Task TASKID="task_\d+_\d+_(m|r)_\d+" TASK_TYPE="\D+" (START_TIME="\d+"|TASK_STATUS="\D+") (FINISH_TIME="\d+")?', line)
        if res:
            record = res.group()
#            print record
            task_info = {}
            id = re.search(r'\btask_\d+_\d+_(m|r)_\d+\b', record).group()
            if hadoop_info.has_key(id):
                task_info = hadoop_info[id]
            else:
                task_info['id'] = id
            task_info['type'] = re.search(r'MAP|REDUCE|SETUP|CLEANUP', record).group()
            tmp = re.search(r'START_TIME="\d+"', record)
            if tmp:
                task_info['start'] = int(re.search(r'\d+', tmp.group()).group())
            tmp = re.search(r'FINISH_TIME="\d+"', record)
            if tmp:
                task_info['stop'] = int(re.search(r'\d+', tmp.group()).group())
#            task_info['duration'] = task_info['stop'] -  taks_info['start']
            tmp = re.search(r'SPLITS="/default-rack/\w+"', line)
            if tmp:
#                print tmp.group()
                task_info['host'] = re.search(r'/default-rack/\w+', tmp.group()).group()
#                print task_info['host']
            hadoop_info[task_info['id']] = task_info

def parse_reduce_task_info(lines):
    for line in lines:
        if re.search(r'SORT_FINISHED', line):
#            print line
            id = re.search(r'\btask_\d+_\d+_r_\d+\b', line).group()
#            if hadoop_info.has_key(id):
            task_info = hadoop_info[id]
#            else:
#                task_info['id'] = id
#            task_info['type'] = re.search(r'MAP|SETUP|CLEANUP', record).group()
#            tmp = re.search(r'START_TIME="\d+"', record)
#            if tmp:
#                task_info['start'] = int(re.search(r'\d+', tmp.group()).group()) - hadoop_info['submit_time']
            tmp = re.search(r'FINISH_TIME="\d+"', line)
            if tmp:
                task_info['stop2'] = int(re.search(r'\d+', tmp.group()).group())
            tmp = re.search(r'SHUFFLE_FINISHED="\d+"', line)
            if tmp:
                task_info['shuffle'] = int(re.search(r'\d+', tmp.group()).group())
            tmp = re.search(r'SORT_FINISHED="\d+"', line)
            if tmp:
                task_info['sort'] = int(re.search(r'\d+', tmp.group()).group())
            tmp = re.search(r'HOSTNAME="/default-rack/\w+"', line)
            if tmp:
#                print tmp.group()
                task_info['host'] = re.search(r'/default-rack/\w+', tmp.group()).group()
#                print task_info['host']
##            task_info['duration'] = task_info['stop'] -  taks_info['start']
#            hadoop_info[task_info['id']] = task_info

def parse_summary(lines):
    summary = {}
    for line in lines:
        if re.search(r'Job JOBID="job_\d+_\d+" FINISH_TIME=', line):
            res = re.search(r'FINISHED_MAPS="\d+"', line)
            if res:
                summary['finished_maps'] =  int(re.search(r'\d+', res.group()).group())
            res = re.search(r'FINISHED_REDUCES="\d+"', line)
            if res:
                summary['finished_reduces'] = int(re.search('\d+', res.group()).group())
            res = re.search(r'FAILED_MAPS="\d+"', line)
            if res:
                summary['failed_maps'] =  int(re.search(r'\d+', res.group()).group())
            res = re.search(r'FAILED_REDUCES="\d+"', line)
            if res:
                summary['failed_reduces'] = int(re.search('\d+', res.group()).group())
            res = re.search(r'[(]TOTAL_LAUNCHED_REDUCES[)][(]Launched reduce tasks[)][(]\d+[)]', line)
            if res:
                summary['total_launch_reduces'] = int(re.search('\d+', res.group()).group())
            res = re.search(r'[(]TOTAL_LAUNCHED_MAPS[)][(]Launched map tasks[)][(]\d+[)]', line)
            if res:
                summary['total_launch_maps'] = int(re.search('\d+', res.group()).group())
            res = re.search(r'[(]RACK_LOCAL_MAPS[)][(]Rack-local map tasks[)][(]\d+[)]', line)
            if res:
                summary['rack_local_maps'] = int(re.search('\d+', res.group()).group())
            res = re.search(r'[(]DATA_LOCAL_MAPS[)][(]Data-local map tasks[)][(]\d+[)]', line)
            if res:
                summary['data_local_maps'] = int(re.search('\d+', res.group()).group())
    hadoop_info['summary'] = summary
#    print summary

def read_hadoop_history_file(filename):
    fp = open(filename, 'r')
    lines = fp.readlines()
    fp.close()
    return lines

hadoop_info = {}


def parse_print(filename):
    hadoop_info.clear()
    history_lines = read_hadoop_history_file(filename)
#    for i in range(0, 10):
#        print history_lines[i]
    parse_hadoop_job_title(history_lines)
    parse_task_info(history_lines)
    parse_reduce_task_info(history_lines)
    parse_summary(history_lines)
#    print hadoop_info
    
    if PRINT_TASK_LIST:
        if PRINT_LABEL:
            print 'task id,type,host,start time,stop time,shuffle end(reduce),sort end(reduce),stop2(reduce)'
        for k, v in hadoop_info.items():
            if k == 'submit_time' or k == 'finish_time' or k == 'launch_time' or k == 'summary':
                continue
#            print v
            if v['type'] == 'REDUCE':
                print '%s,%s,%s,%d,%d,%d,%d,%d' % (v['id'], v['type'], v['host'],\
                    v['start'] - hadoop_info['submit_time'], v['stop'] - hadoop_info['submit_time'],\
                    v['shuffle'] - hadoop_info['submit_time'], v['sort'] - hadoop_info['submit_time'],\
                    v['stop2'] - hadoop_info['submit_time'])
                continue
            if v['type'] == 'SETUP' or v['type'] == 'CLEANUP':
                print '%s,%s,,%d,%d,,,' % (v['id'], v['type'], v['start'] - hadoop_info['submit_time'],\
                v['stop'] - hadoop_info['submit_time'])
                continue
                
            print '%s,%s,%s,%d,%d,,,' % (v['id'], v['type'], v['host'],\
                v['start'] - hadoop_info['submit_time'], v['stop'] - hadoop_info['submit_time'])
    
    if PRINT_BASIC:
        if PRINT_LABEL:
            print 'submit time,launch time,finish time,submit to launch time,launch to finish time'
        print '%d,%d,%d,%d%d' % (hadoop_info['submit_time'], hadoop_info['launch_time'], hadoop_info['finish_time'],\
            hadoop_info['launch_time'] - hadoop_info['submit_time'], hadoop_info['finish_time'] - hadoop_info['submit_time'])
    if PRINT_SUMMARY:
        v = hadoop_info['summary']
        if PRINT_LABEL:
            print 'finished maps,finished reduces,failed maps,failed reduces',
            print 'total launched reduce tasks,rack-local map tasks,launched map tasks,data-local map tasks'
        print '%d,%d,%d,%d,%d,%d,%d,%d' % (v['finished_maps'], v['finished_reduces'], v['failed_maps'], v['failed_reduces'],\
            v['total_launch_reduces'], v['rack_local_maps'], v['total_launch_maps'], v['data_local_maps'])


def go_through_all_dir(dirname):
    if os.path.isdir(dirname):
        entry = os.listdir(dirname)
        os.chdir(dirname)
        for dir in entry:
            go_through_all_dir(dir)
        os.chdir('..')
    elif os.path.isfile(dirname):
        name = os.path.abspath(dirname)
        if re.search(r'[a-zA-Z-]+_\d+_job_\d+_\d+_root_word\+count$', name):
            print name
#            filenames.append(name)
            outname = name + '_trace'
            folder = os.path.dirname(name)
            outfile = os.path.join(folder, outname)
            fp = open(outfile, 'w')
            syssave = sys.stdout
            sys.stdout = fp
            parse_print(name)
            sys.stdout = syssave

filenames = []

def temp(filename):
    fp = open(filename, 'r')
    fileout = filename + '_out'
    fp_out = open(fileout, 'w')
    fp_lines = fp.readlines()
    fp.close()
    for line in fp_lines:
        print >> fp_out, line


if __name__ == "__main__":
#    temp(sys.argv[1])
    filename = os.path.abspath(sys.argv[1])
    if os.path.isdir(filename):
        filedir = filename
    else:
        filedir = os.path.dirname(filename)
#        parse_print(filename)
        sys.exit()
#    print filename
    go_through_all_dir(filename)
#    for filename in filenames:
#        print filename
#        parse_print(filename)
#    parse_print(filename)
