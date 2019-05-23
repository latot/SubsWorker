#!/usr/bin/env python

from SubsWorker.Utility import execute, checkfile
import json
from SubsWorker.Temp import Temp
import os

class MKV:
    def __init__(self, ifile):
        checkfile(ifile)
        self.file = ifile
        self._extract = {}
        t = Temp.getf()
        out = execute('LANG="en_US.utf8" mkvmerge -J "{}" > "{}"'.format(ifile, t.name))
        with open(t.name) as json_data:
            self.data = json.load(json_data)
            json_data.close()
        ext = ['tracks', 'attachments']
#        for j in ext:
#            for i in range(len(self.data[j])):
#                print(j)
#                print(i)
#                self.data[j][i]["extract"] = lambda: self.extract(j, self.data[j][i]['id'])
        Temp.sclose(t)
        for i in self.data['tracks']:
            setattr(self, "if{}".format(i["type"]), True)
    def extract(self, itype, iid, outf = ""):
        if outf == "":
            key = "{}-{}".format(itype, iid)
            if key in self._extract and os.path.isfile(self._extract[key]):
                return self._extract[key]
            else:
                outf = Temp.getf.name
        out = execute('mkvextract {} "{}" "{}":"{}"'.format(itype, self.file, iid, outf))
        self._extract.update({key: outf})
        return outf
