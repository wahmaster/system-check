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

@task
@parallel(pool_size=8)
@excludehosts
def checkupdate():
    env.parallel = True
    with hide('everything'):
        result = run("yum check-update --disablerepo='*artifactory' %s" % (env.excludes), pty=True)
        if result.return_code == 100:
		    print "<font color=yellow>%s needs updating.</font>" % env.host
        elif result.return_code == 0:
            print "<font color=blue>%s does not seem to need any updates</font>" % env.host
        elif result.return_code == 1:
            print "<font color=red>%s returned an error</font>" % env.host

def kernelReport():
    """Report all running kernel versions"""
    env.parallel = True
    with hide('commands'):
        result = run("uname -r")
        redhat = run("cat /etc/redhat-release")
        uptime = run("uptime")
        kernels = run("rpm -q kernel")
        numkern = len(kernels.split('\n'))
        patchable = run("yum check-update --disablerepo='*artifactory' --exclude=puppet* --exclude=sensu --exclude=mongo* --exclude=redis* --exclude=rabbitmq* --exclude=jfrog-artifactory*" ,pty=True)
        if patchable.return_code == 100:
            patches = "True"
        elif patchabel.return_code == 0:
            patches = "False"
        else:
            patches = "Check"
        foo = "\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"" %(env.host, result, redhat, uptime, numkern, patches)
        return foo

@task
@parallel(pool_size=5)
@excludehosts
def get_stats():
    bar = kernelReport()
    print "Stuff: %s" %(bar)
