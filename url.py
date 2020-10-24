import youtube_dl, subprocess, sys
from youtube_search import YoutubeSearch
from urllib.parse import urlparse
from listHelper import *
from pathHelper import *
from os import path

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
	if not uri_validator(url):
		url = f"https://youtube.com/{YoutubeSearch(url, max_results=1).to_dict()[0]['url_suffix']}"

	URL = subprocess.check_output(unwrap(listReplace(['youtube-dl', '--no-playlist', '-f', 'best', 1, '-g', url], 1, ["--cookies", "cookies.txt"] if path.isfile("cookies.txt") else []))).decode('utf-8').split('\n')[0]
	subprocess.check_output(["ffmpeg", '-hide_banner', '-loglevel', 'error', '-y', '-i', URL, '-fs', maxSize, f'{name}.mp4'])