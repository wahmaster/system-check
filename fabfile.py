#!/usr/bin/env python2.7

from __future__ import with_statement
from fabric.api import *
from fabric.contrib import files
from fabric import tasks
from fabric.network import disconnect_all
from fabric.contrib.console import confirm
from functools import wraps
from fabric.colors import red, green
import json
import re
import os
import time

def excludehosts(func):
    def closuref(*args, **kwargs):
        exhosts = json.loads(env.exhosts)
        if exhosts:
            if any(env.host in s for s in exhosts):
                print("<font color=red>Excluding host %s</font>" % (env.host))
                return
        return func(*args, **kwargs)
    # This is necessary so that custom decorator is interpreted as fabric decorator
    # Fabric fix: https://github.com/mvk/fabric/commit/68601ae817c5c26f4937f0d04cb56e2ba8ca1e04
    # is also necessary.
    closuref.func_dict['wrapped'] = func
    return wraps(func)(closuref)

def kernelReport():
    """Report all running kernel versions"""
    with hide('commands'):
        result = run("uname -r")
        redhat = run("cat /etc/redhat-release")
        kernels = run("rpm -q kernel")
        numkern = len(kernels.split('\n'))
        checkpatch = run("yum check-update --disablerepo='*artifactory' %s" % (env.excludes), pty=True)
        if checkpatch.return_code == 100:
            needspatch = "True"
        elif checkpatch.return_code == 0:
            needspatch = "False"
        else:
            needspatch = "Error"
        foo = "\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"\n" %(env.host, result, redhat, numkern, needspatch)
        print "<font color=white>%s: </font><font color=yellow>%s</font>" % (env.host, result)
        print "<font color=white>%s: </font><font color=yellow>%s</font>" % (env.host, redhat)
        print "<font color=white>%s Installed Kernels: </font><font color=yellow>%s</font>" % (env.host, numkern)
        return foo

@runs_once
def setupCSV(var):
    local("rm %s" % var)
    local("echo \"Server\",\"Kernel\",\"Release\",\"Installed Kernels\",\"Needs Patching\" > %s" % var)

@task
@excludehosts
def get_stats():
    """Creates a csv report containing kernel version along with number of installed kernels, uptime and if there are available updates"""
    timstr = time.strftime("%Y%m%d")
    filename1 = "infoReport%s.csv" %(timstr)
    setupCSV(filename1)
    bar = kernelReport()
    f = open(filename1, 'a')
    f.write(bar)
    f.close()
