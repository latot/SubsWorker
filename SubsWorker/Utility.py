#!/usr/bin/env python

from subprocess import Popen, PIPE
import os
import fnmatch

def fd(x, y = 2):
    return float(("{0:." + str(y) + "f}").format(x))

def num2list(start, end, fill = -1):
    if fill == -1: fill = len(str(end))
    r = []
    for i in range(start, end + 1):
        r.append(str(i).zfill(fill))
    return r

def fg(dir_, pattern):
    t = []
    for file in os.listdir(dir_):
        if fnmatch.fnmatch(file, pattern):
            t.append(file)
    if len(t) != 1:
        print(t)
        raise Exception("Error, more than 1 file")
    return t[0]

def fg2(dir_, pattern):
    t = []
    for file in os.listdir(dir_):
        if fnmatch.fnmatch(file, pattern):
            t.append(file)
    return t

def execute(command):
    p = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    return p.returncode, stdout, stderr

def checkfile(file_):
    if not os.path.isfile(file_):
        raise NameError("the file don't exist: {}".format(file_))
