import subprocess, random, shutil, sys, os
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
	e = os.path.splitext(name)

	cmd  = "ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate " + name
	cmd2 = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 " + name
	t = round(eval(subprocess.check_output(cmd ).decode("utf-8")))
	d = round(eval(subprocess.check_output(cmd2).decode("utf-8")))

	os.mkdir(f"YTP{e[0]}")

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
		os.system(f'''ffmpeg -hide_banner -loglevel fatal -y -i {name} -ss {t}    -to {i[0]} -break_non_keyframes 1 YTP{e[0]}/a{index}.mp4''')
		os.system(f'''ffmpeg -hide_banner -loglevel fatal -y -i {name} -ss {i[0]} -to {i[0] + i[1]} -break_non_keyframes 1 YTP{e[0]}/b{index}.mp4''')
		os.system(f'''ffmpeg -hide_banner -loglevel fatal -y -i YTP{e[0]}/b{index}.mp4 -vf reverse{aud} YTP{e[0]}/r{index}.mp4''')
		n.append(f"a{index}.mp4")
		n.append(f"b{index}.mp4")
		n.append(f"r{index}.mp4")
		n.append(f"b{index}.mp4")
		t = i[0] + i[1]
		index += 1
	os.system(f'''ffmpeg -hide_banner -loglevel fatal -y -i {name} -ss {t} -t {d} -break_non_keyframes 1 YTP{e[0]}/e.mp4''')
	n.append('e.mp4')

	f = open(f'YTP{e[0]}/temp.txt','w')
	for i in n:
		f.write(f"file '{i}'\n")
	f.close()

	os.system(f'''ffmpeg -hide_banner -loglevel fatal -f concat -safe 0 -i YTP{e[0]}/temp.txt -c copy _{e[0]}.mp4''')
	os.remove(name)
	os.rename('_'+name, name)
	#shutil.rmtree(e[0])