import subprocess, random, shutil, os

def videoCrasher(videoName = "monke.mp4", appendName = "append.mp4", outputName = "output.mp4"):
	deleteOG = False
	if videoName == outputName:
		os.rename(deleteOG := videoName, videoName := (os.path.split(os.path.abspath(videoName))[0] + '/' + str(random.random()).replace('.', '') + ".mp4"))
	videoName  = os.path.abspath(videoName ).replace('\\', '/')
	outputName = os.path.abspath(outputName).replace('\\', '/')
	appendName = os.path.abspath(appendName).replace('\\', '/')
	dr = os.path.split(os.path.abspath(videoName))[0].replace('\\', '/')
	os.mkdir(tmpDir := (dr + '/' + str(random.random()).replace('.', '')))

	try:
		subprocess.run(["ffmpeg", "-loglevel", "fatal", "-hide_banner", "-y", "-i", videoName, "-pix_fmt", "yuv411p", newVidName := (tmpDir + '/' + os.path.split(videoName)[1] + 'new.mp4')])
		with open(fileName := (tmpDir + '/files.txt'), 'w') as f:
			f.write(f"""file 'file:{newVidName}'\nfile 'file:{appendName}'""")
		subprocess.run(["ffmpeg", "-loglevel", "fatal", "-hide_banner", "-y", "-f", "concat", "-safe", "0", "-i", fileName, "-codec", "copy", outputName])
	except Exception as e:
		print(e)
	shutil.rmtree(tmpDir)
	if deleteOG: os.remove(videoName)