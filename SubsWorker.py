#!/usr/bin/env python

f1='[GJM] Ao no Kanata no Four Rhythm - 01 (BD 1080p) [4342D6A5].mkv'

from subprocess import Popen, PIPE
import tempfile
import os.path
import os
import json
import pysubs2
import argparse
import fnmatch


from scipy.io.wavfile import read
import matplotlib.pyplot as plt
import numpy
from scipy.optimize import fmin
from scipy import signal, fftpack

temp = []

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
        raise NameError("the file don't exist")

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
    for i in range(s*t, len(a)):
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
    # because we are calculating a sample of the audio
    return (c1 if c1 <= l else c1 - l*2)

def open_(file_):
    k, a = read(file_)
    if k != 1000:
        t = tempfile.NamedTemporaryFile(suffix='.wav')
        out = execute('ffmpeg -y -i "{}" -ar 1000 "{}"'.format(file_, t.name))
        k, a = read(t.name)
        t.close()
        if k != 1000: raise(Exception("Error"))
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
    print('time delay: {}'.format(r))
    return r

def to_wav(file_):
    dfile = read_file(file_)
    if dfile['container']['type'] != 'WAV':
        t = tempfile.NamedTemporaryFile(suffix='.wav')
        temp.append(t)
        out = execute('ffmpeg -y -i "{}" -ar 1000 "{}"'.format(file_, t.name))
        return t.name
    else:
        return file_

def audio_sync(sub, file1, file2):
    sub = how_text(sub)
    file1 = to_wav(how_audio(file1))
    file2 = to_wav(how_audio(file2))
    m = audio_delay(file1, file2)
    sub.shift(ms=m)
    return sub

def main(sub, df, o, m = 1, di = False):
    if not di: di = sub
    check_file(sub)
    check_file(df)
    if di: check_file(di)
    if m == 0:
        raise(Exception("not yet"))
    elif m == 1:
        fpost = audio_sync(sub, di, df)
    elif m == 2:
        fpost = sync_text(sub, df, di)
#    fpost.save(o)
    close_subs()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sync subs with others')
    parser.add_argument('sub', help='subtitle to be synced')
    parser.add_argument('-m', '--method', dest='m', default=0, help="0 - Auto, 1 - Audio, 2 - Text")
    parser.add_argument('-di', '--initial_data', dest='di', default=False, help="data of the subs to be synced")
    parser.add_argument('df', help="new data video to sync the subs")
    parser.add_argument('o', help='output file, without extension')
    args = parser.parse_args()
    main(args.sub, args.df, args.o, args.m, args.di)

