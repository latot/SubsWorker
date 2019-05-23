#!/usr/bin/env python

import numpy
from scipy import fftpack

def array_delay(a1, a2):
    l = len(a1)
    if l != len(a2): raise(Exception("rfvale"))
    # We fill with zeros to can detect if we need +t or -t
    a1 = numpy.append(a1, a1*0)
    a2 = numpy.append(a2, a2*0)
    r = len(a1) - len(a2)
    if r > 0:
        a2 = numpy.append(a2, a1[0:r])
    elif r < 0:
        a1 = numpy.append(a1, a2[0:-r])
    a1 = fftpack.fft(a1, axis=0)
    a2 = fftpack.fft(a2, axis=0)
    # FFT convolution
    c1 = numpy.argmax(numpy.abs(fftpack.ifft(-a1.conjugate()*a2, axis=0))) #delay a1 + shift = a2
    # Be careful, this is a circular convolution, we always delay the minimum range possible
    # because we are calculating a sample of the audio, not fully
    return (c1 if c1 <= l else c1 - l*2)

def text_delay(forig, fpost, maxdelay = 2000):
    dorig = how_text(forig)
    dorig.sort()
    dpost = how_text(fpost)
    dpost.sort()
    diff = dorig[0].start - dpost[0].start
    if abs(diff) > maxdelay:
        print("Right File:")
        for i in range(0, 20):
            print("{} - {}".format(i, dorig[i].text.encode("utf-8")))
        print("\nDelayed File:")
        for i in range(0, 20):
            print("{} - {}".format(i, dpost[i].text.encode("utf-8")))
        i1 = int(input('Line for right file:'))
        i2 = int(input('Line for delayed file:'))
    return dorig[i2].start - dpost[i1].start

