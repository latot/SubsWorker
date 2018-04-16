#!/usr/bin/env python

import magic
import enzyme
from subprocess import Popen, PIPE
import tempfile
import os.path
import pysubs2

def check_file(file_):
	if not os.path.isfile(file_):
		raise NameError("the file don't exist")

def read_mkv(file_):
	with open(file_, 'rb') as f:
		return enzyme.MKV(f)

def check_sub(data):
	if len(data.subtitle_tracks) == 0:
		raise NameError("this file don't have any subtitle")

def execute(command):
	p = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
	stdout, stderr = p.communicate()
	return p.returncode, stdout, stderr

def get_mime(file_):
	tmp = magic.from_file(file_, mime=True).decode('utf-8')
	if tmp == "text/plain":
		code, out, error = execute('mkvmerge -i "{}"'.format(file_))
		tmp = str(out).split("(")[-1].split(")")[0]
	return tmp

def get_subs(file_):
	ret = []
	mime = get_mime(file_)
	if mime == "video/x-matroska":
		mkv = read_mkv(file_)
		check_sub(mkv)
		for k in mkv.subtitle_tracks:
			t = tempfile.NamedTemporaryFile()
			code, out, error = execute('mkvextract tracks "{}" {}:"{}"'.format(file_, k.number - 1, t.name))
			if code != 0: raise NameError("error extracting data from {}:\n{}".format(file_, error))
			ret.append([k.number - 1, t])
	elif mime in ("S_TEXT/ASS", "S_TEXT/SSA", "S_TEXT/SRT", "SubRip/SRT"): #"S_HDMV/PGS"
		ret.append([0, file_])
	else:
		raise NameError("error, format not supported")
	return ret

def close_subs(list):
	for i in list:
		i[1].close()

class one_sub:
	def __init__(self, id_, file_, codec_):
		self.id = id_
		self.file = file_
		self.codec_id = codec_

class super_subs:
	def __setitem__(self, key, value):
		self.master[key] = value
	def __getitem__(self, key):
		return self.master[key]
	def __init__(self, file_):
		check_file(file_)
		self.dom = file_
		self.mime = get_mime(file_)
		self.master = []
		if self.mime == "video/x-matroska":
			mkv = read_mkv(file_)
			check_sub(mkv)
			for k in mkv.subtitle_tracks:
				t = tempfile.NamedTemporaryFile()
				code, out, error = execute('mkvextract tracks "{}" {}:"{}"'.format(file_, k.number - 1, t.name))
				if code != 0: raise NameError("error extracting data from {}:\n{}".format(file_, error))
				self.master.append(one_sub(k.number - 1, t, k.codec_id))
		elif self.mime in ("S_TEXT/ASS", "S_TEXT/SSA", "S_TEXT/SRT", "SubRip/SRT"): #"S_HDMV/PGS"
			self.master.append(one_sub(0, file_, self.mime))
		else:
			raise NameError('error, "{}" format not supported'.format(self.mime))

import argparse

parser = argparse.ArgumentParser(
    description='Sync subs with others',
)

parser.add_argument('os', help='subtitle to be synced')
parser.add_argument('ns', help='subtitle with right timing')
parser.add_argument('o', help='output file, without extension')
parser.add_argument('-v', '--video', dest='v', default=False, help="file with high video")

args = parser.parse_args()


check_file(args.os)
check_file(args.ns)

mos = get_subs(args.os)
mns = get_subs(args.ns)

##for now use the first

sos = pysubs2.load(mos[0][1].name)
sns = pysubs2.load(mns[0][1].name)

diff = sns[0].start - sos[0].start
if abs(diff) > 2000:
	print("First File:")
	for i in range(0, 20):
		print("{} - {}".format(i, sos[i].text.encode("utf-8")))
	print("\nSecond File:")
	for i in range(0, 20):
		print("{} - {}".format(i, sns[i].text.encode("utf-8")))
	i1 = int(raw_input('Line for first file:'))
	i2 = int(raw_input('Line for second file:'))
	diff = sns[i2].start - sos[i1].start

sos.shift(ms=diff)
sos.save("{}.{}".format(args.o, sos.format))

close_subs(mos)
close_subs(mns)
