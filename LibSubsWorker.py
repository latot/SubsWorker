#!/usr/bin/env python

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

def f2d(x):
    return float("{0:.2f}".format(x))

def lpos(text, x, y):
    p = text.find("\pos")
    if p == -1: return text
    e = text.find(")", p)
    ss = text[p + 5:e].replace(" ", "").split(",")
    assert(len(ss) == 2)
    return '{}\\pos({},{}){}'.format(text[0:p], float(ss[0]) + x, float(ss[1]) + y, text[e + 1:len(text)])

def pos(sub, x, y):
    for i in range(len(sub)):
        sub[i].text = lpos(sub[i].text, x, y)
    return sub

def resize(ix, iy, fx, fy, sub):
    sub.info['PlayResY'] = fy
    sub.info['PlayResX'] = fx
#    r = min(fx/ix, fy/iy)
    r = fy/iy
    for a in sub.styles.keys():
        sub.styles[a].marginv = round(sub.styles[a].marginv*r)
        sub.styles[a].marginr = round(sub.styles[a].marginr*r)
        sub.styles[a].marginl = round(sub.styles[a].marginl*r)
        sub.styles[a].shadow = f2d(sub.styles[a].shadow*r)
        sub.styles[a].outline = f2d(sub.styles[a].outline*r)
        sub.styles[a].fontsize = f2d(sub.styles[a].fontsize*r)
    return sub

def toass(sub):
    if sub[len(sub) - 3:len(sub)] == "ass": return pysubs2.load(sub)
    s = pysubs2.load(sub)
    s.save("/tmp/tmp.ass")
    ss = pysubs2.load("/tmp/tmp.ass")
    for j in ss.styles:
        if 'backcolor' in dir(s.styles[j]):
            ss.styles[j].outlinecolor = s.styles[j].backcolor
    return ss

def num2list(start, end, fill = -1):
    if fill == -1: fill = len(str(end))
    r = []
    for i in range(start, end + 1):
        r.append(str(i).zfill(fill))
    return r

def merge(ss):
    s1 = ss[0]
    for i_ in range(1, len(ss)):
        i = ss[i_]
        for j in i:
            s1.insert(0, j)
        s1.import_styles(i)
    return s1

def merged(ss, t):
    for i_ in range(len(ss)):
        ss[i_].shift(ms=t[i_])
    return merge(ss)

def mergeda(ss, t):
    for i_ in range(len(ss)):
        ss[_i] = toass(ss[i_])
    return merge(ss, t)

def get_temp(*param):
    t = tempfile.NamedTemporaryFile(*param)
    temp.append(t)
    return t

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

def close_subs():
    for i in temp:
        i.close()

def execute(command):
    p = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    return p.returncode, stdout, stderr

def check_file(file_):
    if not os.path.isfile(file_):
        raise NameError("the file don't exist: {}".format(file_))

def read_file(file_):
    t = tempfile.NamedTemporaryFile()
    c, o, e = execute('LANG="en_US.utf8" mkvmerge -J "{}" > "{}"'.format(file_, t.name))
    with open(t.name) as json_data:
        data = json.load(json_data)
        json_data.close()
    t.close()
    return data

def how_text(file_):
    dfile = read_file(file_)
    type_ = dfile['container']['type']
    if type_ == 'SSA/ASS subtitles':
        return pysubs2.load(file_)
    elif type_ == "Matroska":
        t = get_temp()
        for i in dfile['tracks']:
            if i['type'] == "subtitles":
                if i['codec'] == "SubStationAlpha":
                    execute('mkvextract tracks "{}" "{}":"{}"'.format(file_, i['id'], t.name))
                    return pysubs2.load(t.name)
    raise Exception('Something not supported')

def how_audio(file_):
    dfile = read_file(file_)
    type_ = dfile['container']['type']
    if type_ != 'Matroska':
        if len(dfile['tracks']) == 1:
            type_ = dfile_['tracks'][0]['type']
            if type_ == 'audio':
                return file_
            else:
                raise(Exception("soething weird"))
        else:
            raise(Exception("soething weird2"))
    else:
        t = get_temp()
        for i in dfile['tracks']:
            if i['type'] == "audio":
                execute('mkvextract tracks "{}" "{}":"{}"'.format(file_, i['id'], t.name))
                return t.name
    raise Exception('Something not supported')

#Right file, orig
#Delayed file, post

def sync_text(sub, forig, fpost):
    sub = how_text(sub)
    dorig = how_text(forig)
    dorig.sort()
    dpost = how_text(fpost)
    dpost.sort()
    diff = dorig[0].start - dpost[0].start
    if abs(diff) > 2000:
        print("Right File:")
        for i in range(0, 20):
            print("{} - {}".format(i, dorig[i].text.encode("utf-8")))
        print("\nDelayed File:")
        for i in range(0, 20):
            print("{} - {}".format(i, dpost[i].text.encode("utf-8")))
        i1 = int(input('Line for right file:'))
        i2 = int(input('Line for delayed file:'))
        diff = dorig[i2].start - dpost[i1].start
    print('time delay: {}'.format(diff))
    sub.shift(ms=diff)
    return sub

def oavg2(w, k, t = 10, s = 0):
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

def delay2(a1, a2):
    l = len(a1)
    if l != len(a2): raise(Exception("rfvale"))
    # We fill with zeros to can detect if we need +t or -t
    a1 = numpy.append(a1, a1*0)
    a2 = numpy.append(a2, a2*0)
    a1 = fftpack.fft(a1, axis=0)
    a2 = fftpack.fft(a2, axis=0)
    # FFT convolution
    c1 = numpy.argmax(numpy.abs(fftpack.ifft(-a1.conjugate()*a2, axis=0))) #delay a1 + shift = a2
    # Be careful, this is a circular convolution, we always delay the minimum range possible
    # because we are calculating a sample of the audio, not fully
    return (c1 if c1 <= l else c1 - l*2)

def open_(file_):
    k, a = read(file_)
#    if k != 1000:
#        t = tempfile.NamedTemporaryFile(suffix='.wav')
#        out = execute('ffmpeg -y -i "{}" -ar 1000 "{}"'.format(file_, t.name))
#        k, a = read(t.name)
#        t.close()
#        if k != 1000: raise(Exception("Error"))
    return k, a

def to_mono(a):
    if len(a[0]) == 1: return a
    return a[:,0]/2 + a[:, 1]/2

def audio_delay(file1, file2):
    nor = lambda a: numpy.piecewise(a, [a == 0, a], [0, lambda x: x/abs(x)])
    k1, a1=open_(file1)
    k2, a2=open_(file2)
    a1 = numpy.diff(a1, axis=0)
    a2 = numpy.diff(a2, axis=0)
    m = numpy.max([oavg2(a1, k1), oavg2(a2, k2)])
#    m = numpy.min([len(a1), len(a2)])
    a1 = to_mono(a1)
    a2 = to_mono(a2)
    r = delay2(a1[0:m], a2[0:m])
    #print('time delay: {}'.format(r))
    return r

def to_wav(file_, sample):
    dfile = read_file(file_)
    if dfile['container']['type'] != 'WAV':
        t = tempfile.NamedTemporaryFile(suffix='.wav')
        temp.append(t)
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
