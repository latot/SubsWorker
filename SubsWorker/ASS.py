#!/usr/bin/env python

import pysubs2
from SubsWorker.Utility import num2list
from SubsWorker.Temp import Temp

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
#   Testing, rescale pos function
#    sub = pos(sub, fx/ix, fy/iy, lambda x, y: x*y)
    return sub

def s2ass(sub):
    s = pysubs2.load(sub)
    if s.format == 'ass': return s
    t = Temp.getf(suffix=".ass")
    s.save(t.name)
    ss = pysubs2.load(t.name)
    Temp.sclose(t)
    if s.format == 'ssa':
        for j in ss.styles:
            if 'backcolor' in dir(s.styles[j]):
                ss.styles[j].outlinecolor = s.styles[j].backcolor
    return ss

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
        ss[_i] = s2ass(ss[i_])
    return merge(ss, t)

def lfunc(text, func, x, y, f = lambda x, y: x + y):
    p = text.find(func)
    while p != -1:
        e = text.find(")", p)
        if e == -1: return text
        ss = text[p + 5:e].replace(" ", "").split(",")
        if len(ss) == 2: text = '{}{}({},{}){}'.format(text[0:p], func, f(float(ss[0]), x), f(float(ss[1]), y), text[e + 1:len(text)])
        p = text.find(func, e)
    return text

def gfunc(sub, func, x, y, f = lambda x, y: x + y):
    for i in range(len(sub)):
        sub[i].text = lfunc(sub[i].text, func, x, y, f)
    return sub

def lpos(text, x, y, f = lambda x, y: x + y):
    return lfunc(text, "\pos", x, y, f)

def pos(sub, x, y, f = lambda x, y: x + y):
    return gfunc(sub, "\pos", x, y, f)
