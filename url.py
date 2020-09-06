import subprocess, sys, os
from urllib.parse import urlparse
from pathHelper import *

def downloadVideo(url, name):
	tt = ["--cookies", f] if os.path.isfile(f := "cookies.txt") else None
	# url  = sys.argv[1]
	# name = sys.argv[2]

	downloadName = addPrefix(name, "DOWNLOAD")

	o = urlparse(url)
	if any([i in o.netloc for i in ["youtube", "youtu.be"]]):
		args = ["youtube-dl", "--quiet", "--geo-bypass", "--max-filesize", "25M", "--merge-output-format", "mp4", "-r", "5M", "-f", "best[filesize<25M]", "-o", f"{downloadName}.mp4", url]
		if tt: args[5:5] = tt
		subprocess.check_call(args)
	else:
		subprocess.check_call(["youtube-dl", "--quiet", "--geo-bypass", "--max-filesize", "25M", "--merge-output-format", "mp4", "-r", "5M", "-o", f"{downloadName}.mp4", url])

	os.system(f"""ffmpeg -y -hide_banner -loglevel fatal -i '{downloadName}.mp4' -fs 8M -c copy '{name}.mp4'""")
	os.remove(f"{downloadName}.mp4")