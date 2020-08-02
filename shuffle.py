import subprocess, random, shutil, sys, os

def shuffle(name):
	e = os.path.splitext(name)
	os.mkdir(e[0])
	cmd =  "ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate "+name
	cmd2 = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "+name
	t = round(eval(subprocess.check_output(cmd ).decode("utf-8")))
	d = round(eval(subprocess.check_output(cmd2).decode("utf-8")))

	h = t * d

	m = 0
	os.system(f"ffmpeg -hide_banner -loglevel fatal -i {name} -map 0 -c copy -f segment -segment_time 0.05 -break_non_keyframes 1 {e[0]}/%d.mp4")
	t = os.listdir(e[0])

	ls = list(range(0, len(t) - 1))
	random.shuffle(ls)
	f = open(e[0]+'/temp.txt','w')
	for i in ls:
		f.write(f"file '{i}.mp4'\n")
	f.close()
	c = f'''ffmpeg -hide_banner -loglevel fatal -f concat -safe 0 -i {e[0]}/temp.txt -c copy _{e[0]}.mp4'''
	os.system(c)

	ls = list(range(0, max(1, int(h - 30))))
	random.shuffle(ls)

	os.system(f'''ffmpeg -hide_banner -loglevel fatal -i {name} -i _{e[0]}.mp4 -vf "shuffleframes={' '.join([str(i) for i in ls])}" -map 0:v? -map 1:a? __{name}''')

	#shutil.rmtree(e[0])
	os.remove(name)
	os.rename("__"+name, name)