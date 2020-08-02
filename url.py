import subprocess, sys, os
from urllib.parse import urlparse

url  = sys.argv[1]
name = sys.argv[2]

o = urlparse(url)
if any([i in o.netloc for i in ["youtube", "youtu.be"]]):
	subprocess.call(f'''youtube-dl --quiet --geo-bypass --max-filesize 25M --merge-output-format mp4 -r 5M -f best[filesize<25M] -o DOWNLOAD{name}.mp4 "{url}"''')
else:
	subprocess.call(f'''youtube-dl --quiet --geo-bypass --max-filesize 25M --merge-output-format mp4 -r 5M -o DOWNLOAD{name}.mp4 "{url}"''')

os.system(f"ffmpeg -y -hide_banner -loglevel fatal -i DOWNLOAD{name}.mp4 -fs 8M -c copy {name}.mp4")
os.remove(f"DOWNLOAD{name}.mp4")