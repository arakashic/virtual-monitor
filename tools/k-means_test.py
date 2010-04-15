#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Yanfei Guo"
__date__ ="$Apr 6, 2010 11:25:52 AM$"

import os, sys, re
from math import fabs

#from stat.stats import lmean

ISOTIMEFMT='%Y-%m-%d %X'

def lmean (inlist):
    """
Returns the arithematic mean of the values in the passed list.
Assumes a '1D' list, but will function on the 1st dim of an array(!).

Usage:   lmean(inlist)
"""
    sum = 0
    for item in inlist:
        sum = sum + item
    return sum/float(len(inlist))

def kmeans(input_set, k):
    center_set = []
    output_set = {}
    #init center set
    i = 0
    while i < k:
        center_set.append(float(input_set[i]))
        name = 'set%d' % i
        output_set[name] = [input_set[i]]
        i += 1
    center_set.sort()
#    print center_set
#    print output_set
    #iterative auto-classfication
    input_size = len(input_set)
    for n in range(k, input_size):
        type = 0
        for m in range(0, k):
            list_num = 0
            for tag, list in output_set.items():
                for p in list:
                    if fabs(p - center_set[m]) < fabs(p - center_set[list_num]):
                        name = 'set%d' % m
                        output_set[name].append(p)
                        output_set[tag].remove(p)
                list_num += 1
                        
            if fabs(input_set[n] - center_set[m]) < fabs(input_set[n] - center_set[type]):
                type = m
        name = 'set%d' % type
        output_set[name].append(input_set[n])
        center_set[type] = lmean(output_set[name])
        center_set.sort()
#        print center_set
#        print output_set

    return output_set, center_set



def kmeans_print(filename):
    input = []
    fp = open(filename, 'r')
    lines = fp.readlines()
    fp.close()
    for line in lines:
        items = line.split(',')
        try:
            input.append(float(items[6]))
        except:
            pass

    output, center = kmeans(input, 4)

#    print lines[0].strip() + ',pf_type'
#    for line in lines[1:]:
#        items = line.split(',')
#        try:
#            pf_rate = int(items[4])
#        except:
#            pass
#
#        if pf_rate in output['set0']:
#            print line.strip() + ',0'
#        elif pf_rate in output['set1']:
#            print line.strip() + ',1'
#        elif pf_rate in output['set2']:
#            print line.strip() + ',2'
#        elif pf_rate in output['set3']:
#            print line.strip() + ',3'

#    print output['set0'],
    for name, list in output.items():
        print '%d ' % len(list),
    print center


def go_through_all_dir(dirname):
    if os.path.isdir(dirname):
        entry = os.listdir(dirname)
        os.chdir(dirname)
        for dir in entry:
            go_through_all_dir(dir)
        os.chdir('..')
    elif os.path.isfile(dirname):
        name = os.path.abspath(dirname)
        if re.search(r'output$', name):
            print name
#            filenames.append(name)
            outname = name + '_trace.csv'
            folder = os.path.dirname(name)
            outfile = os.path.join(folder, outname)
            fp = open(outfile, 'w')
            syssave = sys.stdout
            sys.stdout = fp
            kmeans_print(name)
            sys.stdout = syssave

if __name__ == "__main__":
    filename = os.path.abspath(sys.argv[1])
    if os.path.isdir(filename):
        filedir = filename
    else:
        filedir = os.path.dirname(filename)
        kmeans_print(filename)
        sys.exit()
#    print filename
    go_through_all_dir(filename)