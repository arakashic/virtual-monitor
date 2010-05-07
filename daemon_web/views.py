# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="flyxian"
__date__ ="$2010-5-6 16:54:19$"


from django.http import HttpResponse, Http404
from django.template import Template, Context
from django.template.loader import get_template
from django.shortcuts import render_to_response

import datetime

import os, sys

vmlist = [{'name':'cloud1','ip':'192.168.0.1','status':'Running','mem':512,'vcpu':2,'uuid':'0000-00-00-0000-00','mac':'ff:ff:ff:ff:ff:ff'},\
          {'name':'cloud2','ip':'192.168.0.2','status':'Running','mem':512,'vcpu':2,'uuid':'0000-00-00-0000-01','mac':'ff:ff:ff:ff:ff:ff'},\
          {'name':'cloud3','ip':'192.168.0.3','status':'Running','mem':512,'vcpu':2,'uuid':'0000-00-00-0000-02','mac':'ff:ff:ff:ff:ff:ff'},\
          {'name':'cloud4','ip':'192.168.0.4','status':'Running','mem':512,'vcpu':2,'uuid':'0000-00-00-0000-03','mac':'ff:ff:ff:ff:ff:ff'},\
          {'name':'cloud5','ip':'192.168.0.5','status':'Running','mem':512,'vcpu':2,'uuid':'0000-00-00-0000-04','mac':'ff:ff:ff:ff:ff:ff'},\
          {'name':'cloud6','ip':'192.168.0.6','status':'Running','mem':512,'vcpu':2,'uuid':'0000-00-00-0000-05','mac':'ff:ff:ff:ff:ff:ff'},\
          {'name':'cloud7','ip':'192.168.0.7','status':'Running','mem':512,'vcpu':2,'uuid':'0000-00-00-0000-06','mac':'ff:ff:ff:ff:ff:ff'},\
          {'name':'cloud8','ip':'192.168.0.8','status':'Running','mem':512,'vcpu':2,'uuid':'0000-00-00-0000-07','mac':'ff:ff:ff:ff:ff:ff'}]

vmperflist = [{'name':'cloud1','cpu':80,'cpu_avg':80,'iowait':10,'iowait_avg':10,'mem':400,'mem_avg':450,'pf':12000,'pf_avg':13000,'diskrd':1000,'diskwr':500,'netsend':1000,'netrecv':500},\
              {'name':'cloud1','cpu':80,'cpu_avg':80,'iowait':10,'iowait_avg':10,'mem':400,'mem_avg':450,'pf':12000,'pf_avg':13000,'diskrd':1000,'diskwr':500,'netsend':1000,'netrecv':500},\
              {'name':'cloud1','cpu':80,'cpu_avg':80,'iowait':10,'iowait_avg':10,'mem':400,'mem_avg':450,'pf':12000,'pf_avg':13000,'diskrd':1000,'diskwr':500,'netsend':1000,'netrecv':500},\
              {'name':'cloud1','cpu':80,'cpu_avg':80,'iowait':10,'iowait_avg':10,'mem':400,'mem_avg':450,'pf':12000,'pf_avg':13000,'diskrd':1000,'diskwr':500,'netsend':1000,'netrecv':500}]
          
def index(request):
    content = {'vmlist':vmlist,'vmperflist':vmperflist}
    return render_to_response('./index.html', content)

if __name__ == "__main__":
    print "Hello World"