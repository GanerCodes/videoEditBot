import youtube_dl
from pydub import AudioSegment as AS
from requests import get as req_get
from pathHelper import *
from re import search as re_search
from os.path import isfile

def downloadYT(name, url, skip, delay):
    if "t.co" in url:
        url = req_get(url).url

    if (j := re_search(r"[a-zA-Z_\-0-9]{11,}", url)):
        j = "https://youtu.be/" + j.group(0)
    else:
        raise Exception(f"Error attempting to phrase URL {url}")

    exportName = f"{getDir(name)}/TD{getName(name)}.wav"

    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': exportName,
        'noplaylist': True,
        'quiet': True,
        'max-filesize': '20M'
    }

    if isfile((f:="cookies.txt")): ydl_opts['cookiefile'] = f

    ydl = youtube_dl.YoutubeDL(ydl_opts)
    properties = ydl.extract_info(j, download = False)
    if properties["duration"] > 600:
        raise Exception("Video too long to download!")
    ydl.download([j])

    track = AS.from_file(exportName)
    if skip is not None:
        startTime = skip * 1000
        if startTime > len(track) or startTime < 0:
            track = track.reverse()
        else:
            track = track[startTime:]
    if delay is not None:
        track = AS.silent(duration = delay * 1000) + track
    track.export(f"{addPrefix(name, 'BG')}.wav")
    return True