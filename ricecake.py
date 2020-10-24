from pathHelper import *
from subprocess import getoutput
from struct import pack
from random import uniform, randint
from re import finditer, search
from os import system, path, mkdir, rename, remove, rmdir
from itertools import repeat, chain

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def bstream_until_marker(bfilein, bfileout, marker=0, startpos=0):
	chunk = 1024
	filesize = path.getsize(bfilein)
	if marker :
		marker = str.encode(marker)

	with open(bfilein,'rb') as rd:
		with open(bfileout,'ab') as wr:
			for pos in range(startpos, filesize, chunk):
				rd.seek(pos)
				buffer = rd.read(chunk)

				if marker:
					if buffer.find(marker) > 0 :
						marker_pos = search(marker, buffer).start() # position is relative to buffer glitchedframes
						marker_pos = marker_pos + pos # position should be absolute now
						split = buffer.split(marker, 1)
						wr.write(split[0])
						return marker_pos
					else:
						wr.write(buffer)
				else:
					wr.write(buffer)

def ricecake(filein, amount, hasAudio):
	mode = "custom"
	countframes = 1
	positframes = 1
	audio = 1
	firstframe = 1
	kill = 0.7

	pat = getDir(filein)
	e = path.splitext(filein)
	e0 = getName(filein)
	frameCount = int(getoutput(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "default=nokey=1:noprint_wrappers=1", filein]))
	# system(f"ffmpeg -y -hide_banner -loglevel fatal -i '{filein}' -r 30 -g {int(frameCount / 2)} -vf 'fps=30' -keyint_min 1000000 -qscale 0 '{pat}/RC{e0}.avi'")
	getoutput(["ffmpeg", "-y", "-hide_banner", "-loglevel", "fatal", "-i", filein, "-r", "30", "-g", str(int(frameCount / 2)), "-vf", "fps=30", "-keyint_min", "1000000", "-qscale", "0", f"{pat}/RC{e0}.avi"])
	remove(filein)
	filein = f"{pat}/RC{e0}.avi"

	temp_nb = randint(10000, 99999)
	temp_dir = f"{pat}/temp-" + str(temp_nb)
	temp_hdrl = temp_dir +"/hdrl.bin"
	temp_movi = temp_dir +"/movi.bin"
	temp_idx1 = temp_dir +"/idx1.bin"

	mkdir(temp_dir)

	movi_marker_pos = bstream_until_marker(filein, temp_hdrl, "movi")
	idx1_marker_pos = bstream_until_marker(filein, temp_movi, "idx1", movi_marker_pos)
	bstream_until_marker(filein, temp_idx1, 0, idx1_marker_pos)

	with open(temp_movi,'rb') as rd:
		chunk = 1024
		filesize = path.getsize(temp_movi)
		frame_table = []

		for pos in range(0, filesize, chunk):
			rd.seek(pos)
			buffer = rd.read(chunk)
			for m in (finditer(b'\x30\x31\x77\x62', buffer)):
					if audio:
						frame_table.append([m.start() + pos, 'sound'])		
			for m in (finditer(b'\x30\x30\x64\x63', buffer)):
				frame_table.append([m.start() + pos, 'video'])
			frame_table.sort(key=lambda tup: tup[0])
		l = []
		l.append([0,0, 'void'])
		max_frame_size = 0
		for n in range(len(frame_table)):
			if n + 1 < len(frame_table):
				frame_size = frame_table[n + 1][0] - frame_table[n][0]
			else:
				frame_size = filesize - frame_table[n][0]
			max_frame_size = max(max_frame_size, frame_size)
			l.append([frame_table[n][0],frame_size, frame_table[n][1]])

	clean = []
	final = []

	if firstframe:
		for x in l:
			if x[2] == 'video':
		 		clean.append(x)
		 		break

	for x in l:
		clean.append(x)
	final = clean.copy()

	partial = (len(final) / amount)
	if mode == "custom":
		j = 0	
		MI = 0
		while True:
			if j > amount:
				break
			MI += partial
			index = int(MI) % len(final)
			thisFrame = final[index]
			#print(thisFrame)
			if thisFrame[2] != 'video':
				continue

			if hasAudio:
				NA = [i for i in sorted(range(len(final)), key = lambda x: abs(x - index)) if final[i][2] == "sound"]
			times = int(uniform(5, 60))
			if hasAudio:
				r = [final[NA[int(i / 15) % len(NA)]] for i in range(int(times * 1.285))] + [final[index] for i in range(times)]
			else:
				r = [final[index] for i in range(times)]

			final[index:index] = r

			MI = index + len(r)
			j += 1

	cname = '-c' + str(countframes) if int(countframes) > 1 else '' 
	pname = '-n' + str(positframes) if int(positframes) > 1 else ''

	fileout = f"{pat}/O{e0}.avi"

	if path.exists(fileout):
		remove(fileout)

	bstream_until_marker(temp_hdrl, fileout)

	with open(temp_movi, 'rb') as rd:
		filesize = path.getsize(temp_movi)
		with open(fileout, 'ab') as wr:
			wr.write(pack('<4s', b'movi'))
			for x in final:
				if x[0] != 0 and x[1] != 0:
					rd.seek(x[0])
					wr.write(rd.read(x[1]))

	bstream_until_marker(temp_idx1, fileout)

	remove(temp_hdrl)
	remove(temp_movi)
	remove(temp_idx1)
	rmdir(temp_dir)

	# system(f"ffmpeg -y -hide_banner -loglevel fatal -i '{pat}/O{e0}.avi' '{pat}/{e0}.mp4'")
	getoutput(["ffmpeg", "-y", "-hide_banner", "-loglevel", "fatal", "-i", f"{pat}/O{e0}.avi", f"{pat}/{e0}.mp4"])
	remove(f"{pat}/RC{e0}.avi")
	remove(f"{pat}/O{e0}.avi")