from os import path, makedirs
from json import loads
from requests import get
from subprocessHelper import *
import argparse

VBR = "775k"
ABR = "64k"
FILESIZE = "6.3M"

def youtubeSearch(url):
    txt = ""
    counter = 0
    while "ytInitialData" not in txt:
        txt = get(f"https://www.youtube.com/results?search_query={url}").text
        if counter > 5:
            print(f'Found no results for query {url}. Error:', e)
            return False
        counter += 1
    try:
        txt = txt[(start := txt.index("{", start := (txt.index(term := "ytInitialData") + len(term)))): txt.index("};", start) + 1]
        t = loads(txt)["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]
    except Exception as e:
        print(f'Error searching for query {url}. Error:', e)
        return False
    for i in t:
        if next(iter(i)) == "videoRenderer":
            return f"https://youtube.com/watch?v={i['videoRenderer']['videoId']}"
    return False

def is_url(url):
    try:
        return get(url).url
    except:
        return False

def addModifiers(cmd, skip = None, duration = None):
    if skip:
        cmd += ["-ss", str(skip)]
    if duration:
        cmd += ["-t", str(duration)]

def download(name, url, skip = None, delay = None, duration = None, video = True, cookies = "cookies.txt"):
    name = name.replace('\\', '/').replace('//', '/')
    if not path.isdir(folder := path.split(name)[0]): makedirs(folder)
    url = url.replace('\n', '').strip()
    if video: delay = None

    if newUrl := is_url(url):
        url = newUrl
    else:
        if len(url) == 12 and ' ' not in url and get(f"https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/watch?v={url}").text.lower().strip() != "not found":
            url = f"https://youtube.com/watch?v={url}"
        else:
            tmpUrl = url
            url = youtubeSearch(url)
            if not url: return False

    urlCMD = ["youtube-dl", "--no-playlist", "-g"]
    if cookies and path.isfile(cookies): urlCMD += ["--cookies", cookies]
    urlCMD += [url]
    URLs = getout_r(urlCMD)

    if URLs[0] == 0:
        URLs = URLs[1].strip().split('\n')
    else:
        print("URL Error, Return code:", URLs[0])
        return False
    
    videoURL, audioURL = "", ""
    if len(URLs) == 1:
        video = False
        audioURL = URLs[0]
    else:
        videoURL, audioURL = URLs[0], URLs[1]

    ffmpegCommand = ["ffmpeg",  "-y", "-hide_banner", "-loglevel", "error"]
    addModifiers(ffmpegCommand, skip, duration)
    ffmpegCommand += ["-i", audioURL]

    if video:
        addModifiers(ffmpegCommand, skip, duration)
        ffmpegCommand += ["-i", videoURL]
    if delay:
        ffmpegCommand += ["-filter_complex", f"adelay={str(1000 * delay)}:all=true"]
    if VBR:
        ffmpegCommand += ["-b:v", str(VBR)]
    if ABR:
        ffmpegCommand += ["-b:a", str(ABR)]
    if FILESIZE:
        ffmpegCommand += ["-fs", str(FILESIZE)]
    if video and videoURL:
        ffmpegCommand += ["-fflags", "+shortest"]

    ffmpegCommand += [name]
    # print(ffmpegCommand)

    if returnCode(ffmpegCommand) != 0:
        print("Error on download command:", url, skip, delay, duration, video, ffmpegCommand, urlCMD)
        return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Download a video based on a URL or query.")
    parser.add_argument("-o", "--output"  , type = str  , dest = "output"  , help = "Output file name")
    parser.add_argument("-u", "--url"     , type = str  , dest = "url"     , help = "Url OR search query")
    parser.add_argument("-s", "--skip"    , type = float, dest = "skip"    , help = "Skip in video", default = None)
    parser.add_argument("-d", "--duration", type = float, dest = "duration", help = "Max duration of downloaded video", default = None)  
    args = parser.parse_args()
    if not (args.output or args.url):
        parser.error("Error. Output and Url are required.")
    download(args.output, args.url, args.skip, duration = args.duration)