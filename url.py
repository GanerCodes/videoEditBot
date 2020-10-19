import youtube_dl, subprocess, sys, os
from urllib.parse import urlparse
from pathHelper import *

maxSize = "7.5M"

def uri_validator(x): #https://stackoverflow.com/a/38020041
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False

def downloadVideo(url, name):
	url = url.strip()
	if url == '':
		url = "https://youtu.be/Q-Y5_gs6e8Q"
	search = "" if uri_validator(url) else "ytsearch:"
	subprocess.check_output(["ffmpeg", '-hide_banner', '-loglevel', 'error', '-y', '-i', subprocess.check_output(['youtube-dl', '--no-playlist', '-f', 'best', '-g', f"{search}{url}"]).decode('utf-8').split('\n')[0], '-fs', maxSize, f'{name}.mp4'])
		
downloadVideo("https://cdn.discordapp.com/attachments/751568786804572260/764528166000787463/9460095835_1602348114593.mp4", "yeah")