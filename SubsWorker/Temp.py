#!/usr/bin/env python

import tempfile

class Temp:
    tf = set()
    td = set()
    def getf(**param):
        t = tempfile.NamedTemporaryFile(**param)
        Temp.tf.add(t)
        return t
    def getd(**param):
        t = tempfile.TemporaryDirectory(**param)
        Temp.td.add(t)
        return t
    def close():
        for i in Temp.tf:
            i.close()
        for i in Temp.td:
            i.cleanup()
            i._finalizer()
        Temp.tf = set()
        Temp.td = set()
    def sclose(t):
        if t in Temp.tf:
            t.close()
            Temp.tf.remove(t)
        if t in Temp.td:
            t.cleanup()
            t._finalizer()
            Temp.td.remove(t)
    def sclosebyname(t):
        for i in Temp.tf:
            if i.name == t:
                Temp.sclose(i)
                break
        for i in Temp.td:
            if i.name == t:
                Temp.sclose(i)
