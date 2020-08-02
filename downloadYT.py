import youtube_dl, requests, os, re
from pydub import AudioSegment as AS

def downloadYT(name, url, skip, delay):
    if "t.co" in url:
        url = requests.get(url).url
    j = re.search(r"((youtu.be\/|youtube.com\/watch\?v=)[a-zA-Z0-9_-]{10,12})|[a-zA-Z0-9_-]{10,12}", url)
    if j is not None: 
        j = f"https://{'' if '/' in j.group(0) else 'youtu.be/'}{j.group(0)}"
        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': f"{'BG' if (skip is None and delay is None) else 'TD'}{name}.wav",
            'noplaylist': True,
            'quiet': True,
            'max-filesize': '20M'
        }
        ydl = youtube_dl.YoutubeDL(ydl_opts)
        properties = ydl.extract_info(j, download = False)
        if properties['duration'] < 600:
            ydl.download([j])
            if skip is not None or delay is not None:
                track = AS.from_file(f"TD{name}.wav")
                if skip is not None:
                    startTime = skip * 1000
                    if startTime > len(track) or startTime < 0:
                        track = track.reverse()
                    else:
                        track = track[startTime:]
                if delay is not None:
                    track = AS.silent(duration = delay * 1000) + track
                track.export(f"BG{name}.wav")
                os.remove(f"TD{name}.wav")
            return True