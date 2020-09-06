from pathHelper import *
from os import path, mkdir, system, remove, rename
from subprocess import getoutput
from math import floor
from random import uniform as r

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

def ytp(name, itters, hasAudio):
	pat = getDir(name)
	e = path.splitext(name)
	e0 = getName(pat)

	cmd  = f"ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate '{name}'"
	cmd2 = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 '{name}'"
	t = round(eval(getoutput(cmd )))
	d = round(eval(getoutput(cmd2)))

	mkdir(f"{pat}/YTP{e0}")

	points = []
	MT = 0.1

	inc = d / itters
	for i in range(itters * 5):
		time   = r(0.1, r(0.1, r(0.2, 0.6)) * r(r(0, min(10, d / 16)), min(10, d / 6)))
		startPoint = r(MT, MT + inc * 2)
		if startPoint + time > d:
			break
		points.append([startPoint, time])
		MT = startPoint + time

	points = sorted(points)

	t, index = 0, 0
	n = []

	aud = " -af areverse" if hasAudio else ""

	for i in points:
		system(f'''ffmpeg -hide_banner -loglevel error -y -i '{name}' -ss {t}    -to {i[0]} -break_non_keyframes 1 '{pat}/YTP{e0}/a{index}.mp4' ''')
		system(f'''ffmpeg -hide_banner -loglevel error -y -i '{name}' -ss {i[0]} -to {i[0] + i[1]} -break_non_keyframes 1 '{pat}/YTP{e0}/b{index}.mp4' ''')
		system(f'''ffmpeg -hide_banner -loglevel error -y -i '{pat}/YTP{e0}/b{index}.mp4' -vf reverse{aud} '{pat}/YTP{e0}/r{index}.mp4' ''')
		n.append(f"a{index}.mp4")
		n.append(f"b{index}.mp4")
		n.append(f"r{index}.mp4")
		n.append(f"b{index}.mp4")
		t = i[0] + i[1]
		index += 1
	system(f'''ffmpeg -hide_banner -loglevel error -y -i '{name}' -ss {t} -t {d} -break_non_keyframes 1 '{pat}/YTP{e0}/e.mp4' ''')
	n.append('e.mp4')

	f = open(f'{pat}/YTP{e0}/temp.txt','w')
	for i in n:
		f.write(f"file '{i}'\n")
	f.close()

	system(f'''ffmpeg -hide_banner -loglevel error -f concat -safe 0 -i '{pat}/YTP{e0}/temp.txt' -c copy '{pat}/_{e0}.mp4' ''')
	remove(name)
	rename(f"{pat}/_{e0}.mp4", name)
	#shutil.rmtree(e[0])