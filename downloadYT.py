from pytube import YouTube
from pydub import AudioSegment as AS
from requests import get as req_get
from pathHelper import *
from re import search as re_search

def downloadYT(name, url, skip, delay):
    if "t.co" in url:
        url = req_get(url).url

    j = re_search(r"[a-zA-Z_\-0-9]{11,}", url)

    if j is not None:
        j = "https://youtu.be/" + j.group(0)
    else:
        raise Exception(f"Error attempting to phrase URL {url}")

    dwn = YouTube(url)
    if dwn.length > 500:
        raise Exception("Video too long to download!")
        
    dwn.streams.filter(only_audio = True)[0].download(output_path = getDir(name), filename = f"TD{getName(name)}")

    track = AS.from_file(f"{addPrefix(name, 'TD')}.mp4")
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