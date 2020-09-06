from pathHelper import *
from itertools import chain
from shutil import rmtree
from random import uniform, randint, shuffle as randshuf
from pydub import AudioSegment as AS
from math import ceil
from re import sub as re_sub
from os import listdir, system, path, rename, remove, mkdir


NEWFPS = 30
DUR = 30
pre = "-y -hide_banner -loglevel fatal"

class frame():
	def __init__(self, loc, data = None):
		self.loc = loc
		self.data = data

class frameList:
	def __init__(self, length, data = None):
		self.data = [frame(i, data = data) for i in range(length)]
	def __getitem__(self, index):
		return self.data[index]
	def __iter__(self):
		for i in self.data:
			yield i
	def __repr__(self):
		return '-'.join([str(i.loc) for i in self.__iter__()])
	def __len__(self):
		return len(self.data)
	def __setitem__(self, index, value):
		if type(value) == int:
			self.data[index] = frame(value)
		else:
			self.data[index] = value
	def __contains__(self, data):
		return data in [i.loc for i in self.__iter__()]

def shuffle(l):
	randshuf(l)
	return l

def shuffle_slice(x, startIdx, endIdx):
	for i in reversed(range(startIdx+1, endIdx)):
		j = randint(startIdx, i)
		x[i], x[j] = x[j], x[i]

def r(start, stop):
	return int(uniform(start, stop))

def FBOA(l, a, v):
	return next((x for x in l if x[a] == v), None)

def sortByList(list1, list2):
	return [x for _, x in sorted(zip(list2, list1))]

def reverseByChunks(l, s):
	return list(chain.from_iterable([l[max(0, len(l)-i-s):min(len(l), len(l)-i)] for i in range(0, len(l), s)]))

def reverseChunks(l, s):
	return list(chain.from_iterable([l[i+s:i:-1] for i in range(0, len(l), s)]))

def shuffleChunks(l, s):
	return list(chain.from_iterable([l[i:i+s] for i in shuffle(list(range(ceil(len(l) / s))))]))

def stutter(name, para, hasAudio):
	pat = getDir(name)
	e = path.splitext(name)
	e0 = getName(pat)

	fName = f"{pat}/STUTTER_{e0}"
	if path.isdir(fName):
		rmtree(fName)
	mkdir(fName)
	system(f"ffmpeg {pre} -i '{name}' -qscale:v 4 -vf 'fps={NEWFPS}' '{fName}/frame%06d.jpg'")
	if hasAudio:
		system(f"ffmpeg {pre} -i '{name}' '{pat}/ST{e0}.wav'")
	remove(name)
	if hasAudio:
		audio = AS.from_wav(f"{pat}/ST{e0}.wav")
	files = listdir(fName)
	audioFrames = []
	intv = 1000 / NEWFPS
	
	special = []
	frames = frameList(len(files))
	para['maxdur'] = min(len(frames), para['maxdur'])

	def fancySort(amount, f, mindur = para['mindur'], maxdur = para['maxdur'], **args):
		am = len(frames) / max(2, amount)
		minIndex = 0
		for i in range(amount):
			times = r(mindur, maxdur)
			loc = minIndex + round(am) * r(0.7, 1.3)
			if mindur == -1:
				loc = 0
				times = len(frames)
			f(loc, times, **args)
			minIndex = loc + times

	def filter_shuffle(loc, times):
		frames[loc:loc+times] = shuffle(frames[loc:loc+times])
		if hasAudio and para['audioShuffle']:
			for i in range(times):
				if loc + i < len(frames):
					frames[loc + i].data = "shuffle"

	def filter_reverse  (loc, times, intv = 2):
		frames[loc:loc+times] = reverseByChunks(frames[loc:loc+times], intv)

	def filter_duplicate(loc, times, intv = 2):
		times = constrain(times, 0, 120)
		frames[loc:loc] = frames[loc:loc+intv] * ceil(times / max(1, intv))
		if hasAudio and para['audioDuplicate']:
			for i in range(times):
				if loc + i < len(frames):
					frames[loc + i].data = "duplicate"

	if para['shuffle']:   fancySort(para['shuffle'  ], filter_shuffle)
	if para['reverse']:	  fancySort(para['reverse'  ], filter_reverse, intv = r(1, 4))
	if para['duplicate']: fancySort(para['duplicate'], filter_duplicate, intv = r(1, 3))

	if hasAudio:
		audioFrames = AS.silent(duration = 0)
		for i in frames:
			part = audio[round(i.loc * intv) : round((i.loc + 1) * intv)]
			if i.data == "shuffle":
				newAudio = AS.silent(duration = 0)
				pattern = shuffleChunks(list(range(len(part))), int(max(1, 50 - para['audioShuffle'] / 2)))
				for x in pattern:
					newAudio += part[x]
				part = newAudio
			elif i.data == "duplicate":
				part = (part[:para['audioDuplicate']] * ceil(len(part) / max(1, para['audioDuplicate'])))[:len(part)]
			audioFrames += part

	with open(f"{fName}.txt", 'w+') as txt:
		for i in frames:
			txt.write(f"file '{getName(fName)}/{files[i.loc]}'\n")
	if hasAudio:
		audioFrames.export(f"{fName}.wav", format = "wav")
		
	stupididiotretarddumbquote = "'"
	system(f"ffmpeg {pre} -safe 0 -r {NEWFPS} -f concat -i '{fName}.txt' {f'''-i '{fName}.wav{stupididiotretarddumbquote}''' if hasAudio else ''} -vf 'fps={NEWFPS}' -shortest -map 0:v {'-map 1:a?' if hasAudio else ''} '{name}'")
	#rmtree(fName)

def constrain(val, min_val, max_val):
    if val == None:
        return None
    if type(val)     == str:
        val     = float(val    )
    if type(min_val) == str:
        min_val = float(min_val)
    if type(max_val) == str:
        max_val = float(max_val)
    return min(max_val, max(min_val, val))

def intCeil(x):
	return int(ceil(x))

def stutterInputProcess(name, st, hasAudio = True, entireShuffle = False, dur = 30):
	global DUR
	st = re_sub(r"[^0-9.]", "", st)
	DUR = float(dur)
	preset = {
		'reverse': 	 intCeil(2 * DUR / 30),
		'shuffle': 	 intCeil(2 * DUR / 30),
		'duplicate': intCeil(2 * DUR / 30),
		'audioShuffle': None,
		'audioDuplicate': None,
		'mindur': 20,
		'maxdur': 75
	}
	if entireShuffle:
		preset = {
			'reverse': 0,
			'shuffle': 1,
			'duplicate': 0,
			'audioShuffle': None,
			'audioDuplicate': None,
			'mindur': -1,
			'maxdur': -1
		}
	elif st.isnumeric():
		st = intCeil(constrain(int(int(2 * st) / 10), 1, 10) * (DUR / 30))
		preset['reverse'], preset['shuffle'], preset['duplicate'] = st, st, st
	elif '.' in st:
		B = [preset[i] for i in preset]
		B.pop(4)
		st = [int(i) for i in filter(len, st.split('.'))]
		B[:len(st)] = st
		gd = lambda x: intCeil(constrain(x, 0, DUR / 1.2))
		preset['reverse'  ] = gd(B[0])
		preset['shuffle'  ] = gd(B[1])
		preset['duplicate'] = gd(B[2])
		preset['audioShuffle'  ] = constrain(B[3], 0, 100)
		preset['audioDuplicate'] = constrain(B[3], 0, 100)
		preset['mindur'] = max(B[4] - B[4] / 2, 0)
		preset['maxdur'] = B[4] + B[4] / 2
	preset['duplicate'] = min(preset['duplicate'], 10)
	stutter(name, preset, hasAudio)