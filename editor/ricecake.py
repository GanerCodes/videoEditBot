import random, os
from subprocess import call
from pathHelper import *

iframe = bytes.fromhex('0001B0')
pframe = bytes.fromhex('0001B6')
spl = bytes.fromhex('30306463')

def ricecake(inputVideo, outputVideo, chance = 1, dups = 5, speed = True):
	inputVideo, outputVideo = absPath(inputVideo), absPath(outputVideo)

	splPath = os.path.splitext(inputVideo)
	call(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'fatal', '-i', inputVideo, newName := chName(inputVideo, f"RICECAKE{getName(inputVideo)}.avi")])

	with open(newName, 'rb') as f:
		frames = f.read().split(spl)

		frameList = []
		for index, frame in enumerate(frames):
			frame += spl
			if frames[5:8] == iframe:
				frameList += [{'type': 'iframe', 'data': frame}]
			else:
				frameList += [{'type': 'pframe', 'data': frame}]

		iframes = 0
		pframes = 0
		with open(finalTmpName := chName(outputVideo, f"TMP_RICECAKE_{getName(outputVideo)}.avi"), 'wb') as out:
			for i, v in enumerate(frameList):
				if v['type'] == 'iframe': iframes += 1
				if v['type'] == 'pframe': pframes += 1

				if v['type'] == 'pframe' and random.random() < chance:
					for i in range(int(dups)):
						out.write(v['data'])
				else:
					out.write(v['data'])

	if inputVideo == outputVideo: os.remove(inputVideo)

	speedFactor = dups * chance * pframes / (pframes + iframes)
	cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'fatal', '-i', finalTmpName]
	if speed:
		cmd += ['-vf', f'setpts=(1/{speedFactor})*PTS', '-af', f'atempo={speedFactor}']
	cmd += [outputVideo]
	call(cmd)

	os.remove(newName)
	os.remove(finalTmpName)