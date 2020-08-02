import os, subprocess, sys
import requests

auto = False

def shitposter9000(files, quality):
    global auto
    auto = True
    
    vQ = 4 / quality
    aQ = 1 / quality

    t = os.path.splitext(files[0])

    gif = t[1] == ".gif"

    if gif:
        vQ /= 50
        
        os.system(f'''ffmpeg -i {files[0]} _{t[0]}.mp4''')
        os.remove(files[0])
        
        os.system(f'''ffmpeg -i _{t[0]}.mp4 -b:v {vQ}M {t[0]}.mp4''')
        os.remove(f"_{t[0]}.mp4")
        
        files = [t[0]+".mp4"]
        t = os.path.splitext(files[0])

        timecodeBreak(files)
        h = os.path.split(files[0])
        os.remove(files[0]);
        os.rename("_"+files[0], files[0])
    else:
        os.system(f'''ffmpeg -i {files[0]} -b:v {vQ}M -b:a {aQ}M _{t[0]}.mp4''')
        os.remove(files[0])
        files = [t[0]+".mp4"]
        t = os.path.splitext(files[0])
        os.rename(f"_{t[0]}.mp4", files[0])
        
        shitify(files)
        os.remove(files[0]);
        os.rename(f"{t[0]}_Horrible.mp4", files[0])
        
        earrape(files)
        os.remove(files[0]);
        os.rename(f"{t[0]}_loud.mp4", files[0])
        
        timecodeBreak(files)
        h = os.path.split(files[0])
        os.remove(files[0]);
        os.rename("_"+files[0], files[0])

def getAudioTracks(file):
    command = f'''ffprobe "{file}" -hide_banner -loglevel panic -show_entries stream=index -select_streams a -of compact=p=0:nk=1'''
    return len(subprocess.getoutput(command).split('\n'))

def bassnuke(files):
    for f in files:
        t = os.path.splitext(f)
        os.system(f'''ffmpeg -i "{f}" -c:v copy -af bass=g=100:f=100:w=1 "{t[0]}_loud{t[1]}"''')

def earrape(files):
    for f in files:
        t = os.path.splitext(f)
        os.system(f'''ffmpeg -i "{f}" -c:v copy -af acrusher=.1:1:64:0:log "{t[0]}_loud{t[1]}"''')

def timecodeBreak(files):
    global auto

    zero   = bytearray.fromhex("00000000")
    one    = bytearray.fromhex("00000001")
    big    = bytearray.fromhex("7FFFFFFF")
    bigNeg = bytearray.fromhex("80000000")
    huge   = bytearray.fromhex("FFFFFFFF")
    for fileName in files:
        with open(fileName, "rb") as binaryFile:
            byteData = bytearray(binaryFile.read())
        print("Modes:")
        print("    -1")        
        print("    big")
        print("    big negative")
        print("    increasing")
        while True:
            if auto:
                mode = "big"
            else:
                mode = input("Enter a mode: ")
            o = byteData.find(b'mvhd', 0)
            if mode == "-1":
                byteData[o+16:o+20] = one
                byteData[o+20:o+24] = huge
            elif mode == "big":
                byteData[o+16:o+20] = one
                byteData[o+20:o+24] = big
            elif mode == "big negative":
                byteData[o+16:o+20] = one
                byteData[o+20:o+24] = bigNeg
            elif mode == "increasing":
                byteData[o+16:o+20] = one
                byteData[o+20:o+24] = zero
                loc = -1
                while True:
                    loc = byteData.find(b'mdhd', loc + 1)
                    if loc == -1:
                        break
                    byteData[loc+20:loc+24] = zero  
            else:
                print("Error: Not a valid mode!")
                continue
            break
        x = fileName.split('\\')
        #nn = f'''{'/'.join(x[:-1])}/_{x[-1]}'''
        new = open("_"+files[0], 'wb')
        new.write(byteData)

def shitify(files):
    global auto
    if auto:
        p1 = "0.035M"
        p2 = "25k"
    else:
        p1 = input("Enter video bitrate (default 1M): ")
        p2 = input("Enter audio bitrate (default 10k): ")
    if p1 == "":
        p1 = "1M"
    if p2 == "":
        p2 = "10k"
    for f in files:
        t = os.path.splitext(f)
        os.system(f'''ffmpeg -i "{f}" -b:v {p1} -b:a {p2} "{t[0]}_Horrible{t[1]}"''')

def amix(files):
    for f in files:
        t = os.path.splitext(f)
        track = getAudioTracks(f)
        prefix = ''.join([f'[0:a:{i}]' for i in range(track)])
        os.system(f'''ffmpeg -i "{f}" -filter_complex {prefix}amix=inputs={track} -c:v copy "{t[0]}_Amixed{t[1]}"''')

def getAudio(files):
    for f in files:
        t = os.path.splitext(f)
        track = getAudioTracks(f)
        prefix = ''.join([f'[0:a:{i}]' for i in range(track)])
        os.system(f'''ffmpeg -i "{f}" -filter_complex {prefix}amix=inputs={track}[H] -map "[H]" "{t[0]}_AudioOnly.mp3"''')

def trim(files):
    t1 = input("Enter start time (0 is default): ")
    if t1 == "":
        t1 = "0"
    t2 = input("Enter end time (max is default): ")

    for f in files:
        maxTime = float(subprocess.check_output(f'''ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{f}"''', shell=True))
        t = os.path.splitext(f)
        l = str(float(t2) - float(t1))
        if t2 != "":
            os.system(f'''ffmpeg -ss {t1} -t {l} -i "{f}" -c copy -map 0? "{t[0]}_Trimmed{t[1]}"''')
        else:
            os.system(f'''ffmpeg -ss {t1} -i "{f}" -c copy -map 0? "{t[0]}_Trimmed{t[1]}"''')

def compress(files):
    downscale = input("Enter bitrate (higher = smaller files but lower quality, default 24): ")
    for f in files:
        t = os.path.splitext(f)
        os.system(f'''ffmpeg -i "{f}" -vcodec libx264 -crf {downscale} -map 0? "{t[0]}_Compressed{t[1]}"''')

def convert(files, ext):
    for f in files:
        t = os.path.splitext(f)
        os.system(f'''ffmpeg -i "{f}" -map 0? "{t[0]}_Converted.{ext}"''')

def fastConvert(files, ext):
    for f in files:
        t = os.path.splitext(f)
        os.system(f'''ffmpeg -i "{f}" -c copy -map 0? "{t[0]}_FastConverted.{ext}"''')

print("Args: "+','.join(sys.argv))
url = sys.argv[1];
r = requests.get(url, allow_redirects=True)
open(sys.argv[2], 'wb').write(r.content)
shitposter9000(
    [sys.argv[2]],
    min(3500, max(2, int(sys.argv[3])))
)
