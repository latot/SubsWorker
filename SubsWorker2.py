#!/usr/bin/env python

import atexit
from subprocess import Popen, PIPE
import tempfile
import os.path
import os
import json
import pysubs2
import argparse
import fnmatch

from scipy.io.wavfile import read
#import matplotlib.pyplot as plt
import numpy
from scipy.optimize import fmin
from scipy import signal, fftpack

temp = []

def get_temp(*param):
    t = tempfile.NamedTemporaryFile(*param)
    temp.append(t)
    return t

def close_temps():
    for i in temp:
        i.close()

def close_temp(tmp):
    temp.remove(tmp)
    tmp.close()

def exit_handler():
    close_temps()

atexit.register(exit_handler)

def execute(command):
    p = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    #Code, text, error text
    return p.returncode, stdout, stderr

def check_file(file_):
    if not os.path.isfile(file_):
        raise NameError("the file don't exist")

def read_file(file_):
    t = get_temp()
    c, o, e = execute('LANG="en_US.utf8" mkvmerge -J "{}" > "{}"'.format(file_, t.name))
    with open(t.name) as json_data:
        data = json.load(json_data)
        json_data.close()
    close_temp(t)
    return data


