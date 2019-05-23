#!/usr/bin/env python

from scipy.io.wavfile import read as readwav
import numpy

from SubsWorker.Temp import Temp
from SubsWorker.Utility import execute
from SubsWorker.Delay import array_delay

def a2mono(a):
    if len(a[0]) == 1: return a
    d = len(a[0])
    f = a[:,0]/d
    for i in range(1, d):
        f = f + a[:,i]/d
    return f

def audio2wav(file_, sample): 
    if MKV(file_).data['container']['type'] != 'WAV':
        t = Temp.getf(suffix='.wav')
        out = execute('ffmpeg -y -i "{}" -ar {} "{}"'.format(file_, sample, t.name))
        return t.name
    else:
        return file_

def audio_sync(sub, file1, file2, sample = 1000):
    sub = how_text(sub)
    file1 = to_wav(how_audio(file1), sample)
    file2 = to_wav(how_audio(file2), sample)
    m = audio_delay(file1, file2)*1000/sample
    sub.shift(ms=m)
    return sub

def adelay(file1, file2, sample):
    file1 = to_wav(how_audio(file1), sample)
    file2 = to_wav(how_audio(file2), sample)
    ad = audio_delay(file1, file2)
    print(ad*1000/sample)
    return int(ad*1000/sample)

def adelay2(file1, file2, sample):
    file1 = to_wav(file1, sample)
    file2 = to_wav(file2, sample)
    ad = audio_delay(file1, file2)
    return int(ad*1000/sample)

def avg(w, k, t = 10, s = 0):
    a = numpy.abs(w)
    c = numpy.zeros(len(a))
    av = False
    cv = False
    v = numpy.mean(a, axis=0)
    for i in range(s*t*k, len(a)):
        if not av and a[i][0] >= v[0] and a[i][1] >= v[1]: av = True
        if not cv:
            c[0] += a[i][0]
            c[1] += a[i][1]
            if c[0] >= t*k*v[0] and c[1] >= t*k*v[1]:
                cv = True
        if av and cv:
            return i
    raise Exception("Your are requesting somthing")

def audio_delay(file1, file2, _nor = False):
    nor = lambda a: numpy.piecewise(a, [a == 0, a], [0, lambda x: x/abs(x)])
    k1, a1=readwav(file1)
    k2, a2=readwav(file2)
    a1 = numpy.diff(a1, axis=0)
    a2 = numpy.diff(a2, axis=0)
    m = numpy.max([oavg2(a1, k1), oavg2(a2, k2)])
#    m = numpy.min([len(a1), len(a2)])
    a1 = a2mono(a1)
    a2 = a2mono(a2)
    if _nor:
        r = array_delay(nor(a1[0:m]), nor(a2[0:m]))
    else:
        r = array_delay2(a1[0:m], a2[0:m])
    #print('time delay: {}'.format(r))
    return r

