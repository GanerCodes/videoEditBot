from time import time
start_time = time()
import sys, ffmpeg

from traceback  import TracebackException
from subprocess import DEVNULL, STDOUT, check_call, getoutput, run
from traceback  import print_exc
from random     import randrange, uniform, shuffle as randshuffle
from shutil     import rmtree
from pydub      import AudioSegment as AS
from math       import ceil
from PIL        import Image
from os         import listdir, system, rename, remove, path, mkdir, makedirs, chdir
from re         import sub as re_sub

from betterStutter import stutterInputProcess
from downloadYT    import downloadYT
from pathHelper    import *
from addSounds     import addSounds
from fixPrint      import fixPrint
from ricecake      import ricecake
from captions      import normalcaption as capN, impact as capI, poster as capP, cap as capC
from ytp           import ytp

parentPath = path.dirname(path.realpath(sys.argv[0]))

sign = lambda x: (-1 if x < 0 else 1)

def printEx(e):
    fixPrint("".join(TracebackException.from_exception(e).format()))

def r(r1, r2):
    return uniform(r1, r2)

def str_int(n):
    return int(float(n))

def silent_run(command, **kawrgs):
    try:
        check_call(command, stdout = DEVNULL, stderr = STDOUT, **kawrgs)
    except Exception as ex:
        fixPrint(f"Silent_run error:\n", command)
        printEx(ex)

def loud_run(command, **kawrgs):
    try:
        check_call(command, **kawrgs)
    except Exception as ex:
        fixPrint(f"loud_run error:\n", command)
        printEx(ex)

def all_in(l1, l2):
    return all(i in l2 for i in l1)

def trySplitBy(string, keys, times = -1):
    for i in keys:
        if i in string:
            return string.split(i, times)
    return [string]

def remove_prefix(t, pre):
    if t.lower().startswith(pre):
        return t[len(pre):]
    return t

def constrain(val, min_val, max_val):
    if val == None:
        return None
    if type(val)     == str:
        val     = float(val    )
    if type(min_val) == str:
        min_val = float(min_val)
    if type(max_val) == str:
        max_val = float(max_val)
    return min(max_val, max(min_val, val))

def translate(x, s1, e1, s2, e2, bounded = True, f = lambda x: x):
    if bounded:
        x = constrain(x, s1, e1)
    x = s2+(e2-s2)*((e1*f(x)-s1*f(e1))/((e1-s1)*f(e1)))
    return constrain(x, s2, e2)

def getImageRes(path):
    return Image.open(path).size

def getDur(filename):
    return getoutput(f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {filename}")

backslash = '\\'
def getSize(filename):
    cmd = f'''ffprobe -v error -show_entries stream=width,height -of csv=p=0:s=x '{filename.replace(backslash, '/').replace('//', '/')}' '''
    return [i.strip() for i in getoutput(cmd).split('x')]

def checkIfDurationIsUnderTime(name, time):
    nn = name
    try:
        h = float(getDur(name))
        if h > 1000000000 or h < 0:
            nn = f"{getDir(name)}/{getName(name)}TIMECHECK.mp4"
            silent_run(f'''ffmpeg -y -i '{name}' -c copy '{nn}' ''')
            h = float(getDur(nn))
            remove(nn)
        if h < time:
            return True
        else:
            return False
    except Exception as e:
        print("TIMECHECK", e)
        tryToDelete(nn)


def tryToDelete(file):
    if path.isfile(file):
        remove(file)

def notNone(x):
    return x is not None

def lim(x, y, m):
    if x <= m and y <= m:
        return (x, y)
    f = m / max(x, y)
    return (x * f, y * f)

def fv(x):
    return 2 * (int(x) >> 1)

def tryToDeleteDir(dr):
    if path.isdir(dr):
        rmtree(dr)

def removeGarbage(path, keepExtraFiles):
    if keepExtraFiles:
        return
    tryToDeleteDir(path)

def strArgs(args):
    return '|'.join([','.join(['='.join([(str(j)) for j in o]) for o in i]) for i in args])

def forceNumber(n):
    n = re_sub(r'[^0-9.-]', '', n)
    n = n.replace('.', '#', 1).replace('.', '').replace('#', '.')
    n = ('-' if n.startswith('-') else '') + n.replace('-', '')
    if not any([i.isdigit() for i in n]):
        n = n + '1'
    return float(n)

def phraseArgs(args, par):
    final = []
    shorthands = {par[i][2]: i for i in par}
    args = list(filter(None, trySplitBy(args, '|')))[:3]
    for g in range(len(args)):
        group = []
        args[g] = trySplitBy(args[g], ",\n")
        for p in range(len(args[g])):
            args[g][p] = [i.strip() for i in trySplitBy(args[g][p].strip(), "=:; ", 1)]
            if len(args[g][p]) == 0:
                continue
            if len(args[g][p]) == 1:
                args[g][p].append("1")
            args[g][p][0] = args[g][p][0].lower()

            if args[g][p][0] in par:
                pass
            elif args[g][p][0] in shorthands:
                args[g][p][0] = shorthands[args[g][p][0]]
            else:
                continue

            cPar = par[args[g][p][0]]
            if cPar[0] == S:
                pass
            else:
                if args[g][p][1].lower() in ["false", "none"]:
                    continue
                args[g][p][1] = forceNumber(args[g][p][1])

            group.append({
                'name' : args[g][p][0],
                'value': args[g][p][1],
                'order': p
            })
        final.append(group)
    return final

def hp(o):
    print(o)
    return o

def strArgs(args):
    return '|'.join( [','.join([f"{o['name']}-{o['order']}={o['value']}" for o in i]) for i in args] )

def timecodeBreak(file, m):
    zero   = bytearray.fromhex("00000000")
    one    = bytearray.fromhex("00000001")
    big    = bytearray.fromhex("7FFFFFFF")
    bigNeg = bytearray.fromhex("80000000")
    huge   = bytearray.fromhex("FFFFFFFF")
    with open(file, "rb") as binaryFile:
        byteData = bytearray(binaryFile.read())
    o = byteData.find(b'mvhd', 0)
    if m == 1:
        byteData[o+16:o+20] = one
        byteData[o+20:o+24] = huge
    elif m == 2:
        byteData[o+16:o+20] = one
        byteData[o+20:o+24] = big
    elif m == 3:
        byteData[o+16:o+20] = one
        byteData[o+20:o+24] = bigNeg
    elif m == 4:
        byteData[o+16:o+20] = one
        byteData[o+20:o+24] = zero
        loc = -1
        while True:
            loc = byteData.find(b'mdhd', loc + 1)
            if loc == -1:
                break
            byteData[loc+20:loc+24] = zero  
    x = file.split('\\')
    new = open(file, 'wb')
    new.write(byteData)

def destroy(file, groupData, par, groupNumber = 0, parentPath = "..", newExt = "mp4", toVideo = False, toGif = False, disallowTimecodeBreak = False, HIDE_FFMPEG_OUT = True, HIDE_ALL_FFMPEG = True, SHOWTIMER = False, fixPrint = fixPrint):
    videoFX = ['playreverse', 'hmirror', 'vmirror', 'lag', 'rlag', 'shake', 'fisheye', 'zoom', 'bottomtext', 'toptext', 'normalcaption', 'cap', 'topcaption', 'bottomcaption', 'hypercam', 'bandicam', 'deepfry', 'hue', 'hcycle', 'speed', 'reverse', 'wscale', 'hscale', 'sharpen', 'watermark', 'framerate', 'invert', 'wave', 'waveamount', 'wavestrength']
    audioFX = ['pitch', 'reverb', 'earrape', 'bass', 'mute', 'threshold', 'crush', 'wobble', 'music', 'sfx', 'volume']

    d = {i: None for i in par}
    for i in groupData:
        d[i['name']] = i['value']

    properFileName = file
    currentPath = path.abspath('')
    pat = getDir(file)
    e0  = getName(file)

    resetTime = True
    ctt = 0
    def timer(msg = 'Duration'):
        if not SHOWTIMER:
            return
        if resetTime:
            ctt = time()
            resetTime = not resetTime
        else:
            print(f"{msg}: {time() - ctt}")
            resetTime = not resetTime

    def getOrder(n):
        for i in groupData:
            if i['name'] == n:
                return i['order']
        return None

    def makeAudio(pre, dr):
        silent_run(["sox", "-n", "-r", "16000", "-c", "1", f"{pat}/{pre}{e0}.wav", "trim", "0.0", str(dr)])

    def qui(t):
        t = t.global_args("-hide_banner")
        if HIDE_FFMPEG_OUT:
            return t.global_args('-loglevel', 'fatal' if HIDE_ALL_FFMPEG else 'error')
        else:
            return t

    def applyBitrate(pre, VBR = None, ABR = None, **exArgs):
        if notNone(VBR):
            exArgs.update(video_bitrate = str(VBR))
        if notNone(d['abr']):
            exArgs.update(audio_bitrate = str(ABR))
        if hasAudio:
            return qui(ffmpeg.output(video, audio, f"{pat}/{pre}{e0}.{getExt(newName)}", **exArgs))
        else:
            return qui(ffmpeg.output(video       , f"{pat}/{pre}{e0}.{getExt(newName)}", **exArgs))

    def removeAudioFilters():
        nonlocal d
        for i in audioFX: d[i] = None

    e = path.splitext(file)
    ST, ET = None, None
    oldFormat = e[1]
    imageArray = [".png", ".jpg", ".jpeg"]

    if e[1] in imageArray:
        #-hide_banner -loglevel {"fatal" if HIDE_ALL_FFMPEG else "error"}
        #print(file,'->',f"{pat}/{e0}.mp4")
        #loud_run(["ffmpeg", "-framerate", "1", f"{file}", "-c:v", "libx264", "-vf", f"scale=w=ceil((iw)/2)*2:h=ceil((ih)/2)*2{',fps=3' if toVideo else ''}", "-pix_fmt", "yuv420p", "-max_muxing_queue_size", "1024", f"{pat}/{e0}.mp4"])
        system(f''' ffmpeg -hide_banner -loglevel error -framerate '1' -i '{file}' -c:v 'libx264' -r '2' -vf 'scale=w=ceil((iw)/2)*2:h=ceil((ih)/2)*2{',fps=3' if toVideo else ''}' -pix_fmt 'yuv420p' -max_muxing_queue_size '1024' '{pat}/{e0}.mp4' ''')

        remove(file)
        file = f"{pat}/{e0}.mp4"
        e = path.splitext(file)
        if toVideo:
            d['holdframe'] = 10
        else:
            removeAudioFilters()
            removeFilters = "ytp,datamosh,clonemosh,ricecake,shake,stutter,shuffle,lag".split(',')
            for i in removeFilters:
                d[i] = None
    else:
        toVideo = False

    filtText = ""
    try:
        width, height = getSize(file)
        if int(width + height) > 800 or int(width) % 2 != 0 or int(height) % 2 != 0:
            filtText = "-vf 'scale=2*ceil(trunc(iw*480/ih)/2):480' "
    except Exception as ex:
        fixPrint("Error near 302:", ex)
        pass

    startText, endText = "", ""
    if notNone(d['start']):
        d['start'] = constrain(float(d['start']), 0, 30000) + 3.5 / 30
        ST = d['start']
        startText = f"-ss {ST} "
    if notNone(d['end']):
        d['end'] =   constrain(float(d['end'  ]), 0, 30000)
        ET = d['end']
        endText = f"-to {max(0.1, d['end'])} "
    system(f'''ffmpeg -hide_banner -loglevel error -i '{e[0]}{e[1]}' {startText}{endText}-reset_timestamps 1 -break_non_keyframes 1 -max_muxing_queue_size 1024 -preset veryfast {filtText}'{pat}/RFM{e0}.mp4' ''')
    if notNone(d['selection']):
        if ST:
            system(f'''ffmpeg -hide_banner -loglevel error -i "{e[0]}{e[1]}" -t {ST} -reset_timestamps 1 -break_non_keyframes 1 -max_muxing_queue_size 1024 -preset veryfast {filtText}'{pat}/START_{e0}.mp4' ''')
        if ET:
            system(f'''ffmpeg -hide_banner -loglevel error -i "{e[0]}{e[1]}" -ss {ET} -reset_timestamps 1 -break_non_keyframes 1 -max_muxing_queue_size 1024 -preset veryfast {filtText}'{pat}/END_{e0}.mp4' ''')

    remove(file)
    file = f"{pat}/{e0}.mp4"
    rename(f"{pat}/RFM{e0}.mp4", file)
    e = path.splitext(file)

    newName = e[0]+".mp4"

    DURATION = getDur(newName)
    hhh = getoutput(f'''ffprobe -v error -of flat=s_ -select_streams 1 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 '{newName}' ''')
    width, height = getSize(newName)

    vidHasAudio = True
    hasAudio = True
    audio = None

    if notNone(d['holdframe']):
        d['holdframe'] = constrain(d['holdframe'], 0.1, 12)
        system(f"""ffmpeg -hide_banner -loglevel error -i '{newName}' -frames:v 1 '{pat}/FIRST_FRAME_{e0}.png'""")
        video = ffmpeg.input(f"{pat}/FIRST_FRAME_{e0}.png", loop = 1, t = d['holdframe'])
        DURATION = d['holdframe']

    if toGif or toVideo or hhh == "null" or hhh.strip() == "" or "no streams" in hhh:
        vidHasAudio = False

    if toGif:
        vidHasAudio = False
        hasAudio = False
        removeAudioFilters()
    elif not vidHasAudio:
        if (notNone(d['sfx']) or notNone(d['music'])):
            makeAudio("GEN", DURATION)
            audio = ffmpeg.input(f"{pat}/GEN{e0}.wav")
            hasAudio = True
        else:
            hasAudio = False
            removeAudioFilters()
    else:
        if notNone(d['holdframe']):
            makeAudio("HFA", d['holdframe'])
            audio = ffmpeg.input(f"{pat}/HFA{e0}.wav")

    orderedVideoFX = sorted(filter(lambda x: notNone(d[x]), videoFX), key=getOrder)
    orderedAudioFX = sorted(filter(lambda x: notNone(d[x]), audioFX), key=getOrder)
    if "mute" in orderedAudioFX:
        orderedAudioFX = orderedAudioFX[orderedAudioFX.index("mute"):]

    s = ffmpeg.input(file)

    if notNone(d['holdframe']):
        if not toVideo:
            audio = ffmpeg.filter([audio, s.audio], "amix", duration = "first")
            hasAudio = True
    else:
        video = s.video
        if vidHasAudio:
            audio = s.audio
            hasAudio = True
    
    video = video.filter("scale", w = f"ceil((iw)/2)*2", h = f"ceil((ih)/2)*2")
    
    if notNone(d['abr']):
        d['abr'] = 100 + 1000 * constrain(100 - d['abr'], 1, 100)
    if notNone(d['vbr']):
        d['vbr'] = 100 + 2000 * constrain(100 - d['vbr'], 2, 100)

    if all_in(["topcaption", "bottomcaption"], orderedVideoFX):
        orderedVideoFX.remove("bottomcaption")
    if all_in(["toptext", "bottomtext"], orderedVideoFX):
        orderedVideoFX.remove("bottomtext")
    if all_in(["wscale", "hscale"], orderedVideoFX):
        orderedVideoFX.remove("hscale")
    if all_in(["hue", "hcycle"], orderedVideoFX):
        orderedVideoFX.remove("hcycle")

    for i in [o for o in ["waveamount", "wavestrength"] if o in orderedVideoFX]:
        if "wave" in orderedVideoFX:
            orderedVideoFX.remove(i)
        else:
            orderedVideoFX[orderedVideoFX.index(i)] = "wave"

    if any(orderedVideoFX):
        def playreverse():
            nonlocal video, audio
            VS = video.split()
            video = VS[0]
            newVideo = VS[1].filter("reverse")
            if d['playreverse'] == 2:
                video = ffmpeg.concat(newVideo, video)
            else:
                video = ffmpeg.concat(video, newVideo)
            if hasAudio:
                APART = audio.asplit()
                audio = APART[0]
                newAudio = APART[1].filter("areverse")
                if d['playreverse'] == 2:
                    audio = ffmpeg.concat(newAudio, audio, v = 0, a = 1)
                else:
                    audio = ffmpeg.concat(audio, newAudio, v = 0, a = 1)
        
        def hmirror():
            nonlocal video, audio
            v2 = video.split()
            if str_int(d['hmirror']) >= 2:
                flip = v2[1].filter("crop", x = "in_w/2", out_w = "in_w/2").filter("hflip")
                video = v2[0].overlay(flip)
            else:
                flip = v2[1].filter("crop", x = 0, out_w = "in_w/2").filter("hflip")
                video = v2[0].overlay(flip, x = "main_w/2")

        def vmirror():
            nonlocal video, audio
            v2 = video.split()
            if str_int(d['vmirror']) >= 2:
                flip = v2[1].filter("crop", y = "in_h/2", out_h = "in_h/2").filter("vflip")
                video = v2[0].overlay(flip)
            else:
                flip = v2[1].filter("crop", y = 0, out_h = "in_h/2").filter("vflip")
                video = v2[0].overlay(flip, y = "main_h/2")

        def lag():
            nonlocal video, audio
            if d['lag'] < 0:
                d['lag'] = 2 * int(translate(abs(d['lag']), 1, 100, 2, 15))
                t = [str(i) for i in range(int(d['lag']))]
                randshuffle(t)
                frameOrder = '|'.join(t)
            else:
                d['lag'] = int(translate(d['lag'], 1, 100, 2, 15)) + 2
                frameOrder = '|'.join([str(v if i % 2 == 0 else d['lag'] - v) for i, v in enumerate(range(d['lag']))])
            video = video.filter("shuffleframes", frameOrder)

        def rlag():
            nonlocal video, audio
            d['rlag'] = constrain(int(d['rlag']), 1, 120)
            video = video.filter("random", d['rlag'])

        def shake():
            nonlocal video, audio
            d['shake'] = translate(d['shake'], 0, 100, 1.00125, 1.1, f = lambda x: x**1.7)
            video = video.filter("crop", f"in_w/{d['shake']}", f"in_h/{d['shake']}", "(random(0)*2-1)*in_w", "(random(1)*2-1)*in_h")

        def fisheye():
            nonlocal video, audio
            d['fisheye'] = int(constrain(d['fisheye'], 1, 2))
            for i in range(d['fisheye']):
                video = video.filter("v360" , input = "equirect", output = "ball")
                video = video.filter("scale", w = width, h = height)
            video = video.filter("setsar", r = 1)
        
        def zoom():
            nonlocal video, audio
            flag = False
            if d['zoom'] < 0:
                d['zoom'] = abs(d['zoom'])
                flag = True
            d['zoom'] = constrain(d['zoom'], 1, 15)
            video = video.filter("crop", f"iw/{d['zoom']}", f"ih/{d['zoom']}")
            zoomargs = ["scale", f"in_w*{d['zoom']}", f"in_h*{d['zoom']}"]
            if not flag:
                video = video.filter(*zoomargs)
            else:
                video = video.filter(*zoomargs, flags = "neighbor")

        def toptext():
            nonlocal video, audio, width, height
            capI(int(width), int(height), toptext = d['toptext'], bottomtext = d['bottomtext']).save(f"{pat}/impact{e0}.png")
            video = video.overlay(ffmpeg.input(f"{pat}/impact{e0}.png"))

        def topcaption():
            nonlocal video, audio, width, height
            capP(int(width), int(height), cap = d['topcaption'], bottomcap = d['bottomcaption']).save(f"{pat}/poster{e0}.png")
            ms = "main_w" if width < height else "main_h"
            video = ffmpeg.input(f"{pat}/poster{e0}.png").overlay(video, x = f"min(main_w,main_h)/20+0.5", y = f"min(main_w,main_h)/20+0.5")
            width, height = getSize(f"{pat}/poster{e0}.png")

        def normalcaption():
            nonlocal video, audio, width, height
            capN(int(width), int(height), cap = d['normalcaption']).save(f"{pat}/normalcaption{e0}.png")
            video = ffmpeg.input(f"{pat}/normalcaption{e0}.png").filter("pad", h = f"(ih+{height})+mod((ih+{height}), 2)").overlay(video, y = f"(main_h-{height})")
            height = str(int(height) + getImageRes(f"{pat}/normalcaption{e0}.png")[1])
            
        def cap():
            nonlocal video, audio, width, height
            capC(int(width), int(height), cap = d['cap']).save(f"{pat}/cap{e0}.png")
            video = ffmpeg.input(f"{pat}/cap{e0}.png").filter("pad",h=f"(ih+{height})+mod((ih+{height}), 2)").overlay(video, y = f"(main_h-{height})")
            height = str(int(height) + getImageRes(f"{pat}/cap{e0}.png")[1])

        def hypercam():
            nonlocal video, audio
            video = video.overlay(ffmpeg.input(f"{parentPath}/images/watermark/hypercam.png").filter("scale", w = width, h = height))

        def bandicam():
            nonlocal video, audio
            video = video.overlay(ffmpeg.input(f"{parentPath}/images/watermark/bandicam.png").filter("scale", w = width, h = height))

        def watermark():
            nonlocal video, audio, height
            height = int(height)
            d['watermark'] = ceil(constrain(d['watermark'], 1, 100) / 4.5)
            j = f"{parentPath}/images/watermark"
            watermarks = [f"{j}/{i}" for i in listdir(j)]
            t = [watermarks[int(r(0, len(watermarks)))] for i in range(d['watermark'])]
            cb, ch = True, True
            for i in t:
                if getName(i) in ["9gag", "memebase", "ifunny", "laugh"]:
                    w, h = getImageRes(i)
                    height += h
                    nn = ffmpeg.filter_multi_output([ffmpeg.input(i), video], "scale2ref", w='iw',h=f"iw * {(h / w)}")
                    video = nn[1].filter("pad", "iw", f"ih+(iw * {h / w})").overlay(nn[0], x = 0, y = f"main_h - (main_w * {h / w})")
                if getName(i) == "mematic":
                    w, h = getImageRes(i)
                    height += h
                    nn = ffmpeg.filter_multi_output([ffmpeg.input(i), video], "scale2ref", w='iw / 3',h=f"iw / 3 * {(h / w)}")
                    video = nn[1].overlay(nn[0], x = "main_w * 0.05", y = "main_h * 0.95")
                if getName(i) == "reddit":
                    nn = ffmpeg.filter_multi_output([ffmpeg.input(i), video], "scale2ref", w = "iw", h = "ih")
                    video = nn[1].overlay(nn[0])
                if cb and getName(i) == "bandicam":
                    bandicam()
                    cb = False
                if ch and getName(i) == "hypercam":
                    hypercam()
                    ch = False
            height = str(height)

        def deepfry():
            nonlocal video, audio
            q = 2 * constrain(d['deepfry'] * 10, 0, 1000)
            if q > 1000:
                q = -q
            video = video.filter("eq", saturation = 1 + (d['deepfry'] / 100), contrast = 1 + q / 10)

        def framerate():
            nonlocal video, audio
            video = video.filter("fps", constrain(d['framerate'], 1, 30))

        def invert():
            nonlocal video, audio
            video = video.filter("negate")

        def hue():
            nonlocal video, audio
            if d['hue'] is None:
                d['hue'] = 0
            else:
                d['hue'] = int(3.6 * constrain(d['hue'], 0, 100))
            if d['hcycle'] is None:
                d['hcycle'] = 0
            else:
                d['hcycle'] = constrain(d['hcycle'], 0, 100) / 10
            video = video.filter("hue", h = f'''{d['hue']} + ({d['hcycle']}*360*t)''')

        def speed():
            nonlocal video, audio
            if d['speed'] < 0:
                d['reverse'] = 1
            q = constrain(abs(d['speed']), 0.5, 25)
            video = video.filter("setpts", (str(1 / q)+"*PTS"))
            if hasAudio:
                audio = audio.filter("atempo", q)

        def reverse():
            nonlocal video, audio
            video = video.filter("reverse")
            if hasAudio:
                audio = audio.filter("areverse")

        def wscale():
            nonlocal video, audio
            scaleX = constrain(ceil(str_int(d['wscale']) / 2) * 2, -600, 600) if notNone(d['wscale']) else "iw"
            scaleY = constrain(ceil(str_int(d['hscale']) / 2) * 2, -600, 600) if notNone(d['hscale']) else "ih"
            if scaleX != "iw":
                if scaleX < 0:
                    video = video.filter("hflip")
                scaleX = max(32, abs(scaleX))
                width = str(scaleX)
            if scaleY != "ih":
                if scaleY < 0:
                    video = video.filter("vflip")
                scaleY = max(32, abs(scaleY))
                height = str(scaleY)
            video = video.filter("scale", w = scaleX, h = scaleY, flags = "neighbor")

        def sharpen():
            nonlocal video, audio

            kw = {}
            if d['sharpen'] < 0:
                d['sharpen'] = abs(d['sharpen'])
                kw["flags"] = "neighbor"
            d['sharpen'] = translate(d['sharpen'], 0, 100, 0.99, 50, f = lambda x: x**3)

            video = video.filter("scale", w = f"iw/{d['sharpen'] + 1}", h = f"ih/{d['sharpen'] + 1}", **kw)
            a = int(d['sharpen'])
            for x in [1 for i in range(a)]+[d['sharpen'] - a]:
                video = video.filter('cas', x)
            video = video.filter("scale", w = f"iw*{d['sharpen'] + 1}", h = f"ih*{d['sharpen'] + 1}", **kw).filter("scale", w = "iw+mod(iw,2)", h = "ih+mod(ih,2)", flags = "neighbor")

        def wave():
            nonlocal video, audio
            if notNone(d['wave']):
                d['wave'] = constrain(d['wave'], -100, 100)
            else:   
                d['wave'] = 0
            if notNone(d['waveamount']):
                d['waveamount'] = constrain(d['waveamount'], 1, 100)
            else:
                d['waveamount'] = 10
            if notNone(d['wavestrength']):
                d['wavestrength'] = constrain(d['wavestrength'], 1, 100)
            else:
                d['wavestrength'] = 20
            v = f"p(X,floor(Y+sin(T*{d['wave']/10}+X*{d['waveamount']/100})*{d['wavestrength']}))"
            video = video.filter("geq", r = v, g = v, b = v)

        vidBind = {
            'playreverse': playreverse,
            'hmirror': hmirror,
            'vmirror': vmirror,
            'lag': lag,
            'rlag': rlag,
            'shake': shake,
            'fisheye': fisheye,
            'zoom': zoom,
            'bottomtext': toptext,
            'toptext': toptext,
            'normalcaption': normalcaption,
            'cap': cap,
            'topcaption': topcaption,
            'bottomcaption': topcaption,
            'hypercam': hypercam,
            'bandicam': bandicam,
            'deepfry': deepfry,
            'hue': hue,
            'hcycle': hue,
            'speed': speed,
            'reverse': reverse,
            'wscale': wscale,
            'hscale': wscale,
            'sharpen': sharpen,
            'watermark': watermark,
            'framerate': framerate,
            'invert': invert,
            'wave': wave
        }

        for i in orderedVideoFX:
            vidBind[i]()

    if any(orderedAudioFX):
        if notNone(d['volume']):
            d['volume'] = constrain(d['volume'], 0, 2000)
            audio = audio.filter("volume", d['volume'])
            orderedAudioFX.remove('volume')

        qui(audio.output(f"{pat}/{e0}.wav").overwrite_output()).run()

        def exportSox(INPRE, OUTPRE):
            nonlocal SOXCMD
            SOXCMD = ["sox", f"{pat}/{INPRE}{e0}.wav", f"{pat}/{OUTPRE}{e0}.wav"] + SOXCMD
            silent_run(SOXCMD)
            SOXCMD = []

        def mute(SOXCMD, AUDPRE):
            SOXCMD += ['gain', "-1000"]
            return AUDPRE
        def threshold(SOXCMD, AUDPRE):
            n = -(50 - constrain(d['threshold'], 1, 100) / 2)
            th = str(n)
            SOXCMD += ["compand", ".1,.2", f"-inf,{float(th)-0.1},-inf,{th},{th}", "0", "-100", ".1"]
            return AUDPRE
        def bass     (SOXCMD, AUDPRE):
            d['bass'] = translate(d['bass'] / 100, -1, 1, -1000, 1000, f = lambda x: sign(x)*(abs(x)/20 if abs(x) < 0.7 else ((abs(x)-0.2675)**4)))
            SOXCMD += ["bass", str(d['bass'])]
            return AUDPRE
        def earrape  (SOXCMD, AUDPRE):
            d['earrape'] = constrain(d['earrape'], 0, 100) * 10
            SOXCMD += ["gain", str(d['earrape'])]
            return AUDPRE
        def pitch    (SOXCMD, AUDPRE):
            d['pitch'] = 12 * int(constrain(d['pitch'], -100, 100))
            SOXCMD += ["pitch", str(d['pitch'])]
            return AUDPRE
        def reverb   (SOXCMD, AUDPRE):
            d['reverb'] = 25 + constrain(d['reverb'], 0, 100) * (3 / 4 - 0.01)
            rvb, rbd = str(d['reverb']), '0'
            if d['reverbdelay'] is not None:
                rbd = str(5 * constrain(float(d['reverbdelay']), 0, 99.9))
            SOXCMD += ["reverb", rvb, rvb, rvb, rvb, rbd, str(d['reverb'] / 10)]
            return AUDPRE
        def crush     (SOXCMD, AUDPRE):
            if len(SOXCMD) > 0:
                exportSox(AUDPRE, "PRE_CRUSH")
                AUDPRE = "PRE_CRUSH"
            d['crush'] = int(translate(d['crush'], 0, 100, 1, 10))
            ASI = AS.from_file(f"{pat}/{AUDPRE}{e0}.wav", "wav")
            ASN = AS.silent(duration = 0)
            n1 = (2 ** d['crush'])
            for i in range(0, len(ASI), n1):
                ASN += ASI[n1 * (i >> d['crush'])] * n1
            ASN.export(f"{pat}/CRUSH{e0}.wav", format = "wav")
            return "CRUSH"
        def wobble    (SOXCMD, AUDPRE):
            if len(SOXCMD) > 0:
                exportSox(AUDPRE, "PRE_WOB")
                AUDPRE = "PRE_WOB"
            d['wobble'] = ceil(translate(d['wobble'], 0, 100, 1, 100, f = lambda x: x ** 3))
            wobAud = qui(ffmpeg.input(f"{pat}/{AUDPRE}{e0}.wav").filter("vibrato", d['wobble'], 1).output(f"{pat}/WOBBLE{e0}.wav")).run()
            return "WOBBLE"
        def music(SOXCMD, AUDPRE):
            try:
                if notNone(d['musicdelay']):
                    d['musicdelay'] = constrain(d['musicdelay'], 0, DURATION)
                if downloadYT(f"{pat}/{e0}", d['music'], d['musicskip'], d['musicdelay']):
                    if len(SOXCMD) > 0:
                        exportSox(AUDPRE, "PRE_MUSIC")
                        AUDPRE = "PRE_MUSIC"
                    qui(ffmpeg.filter([ffmpeg.input(f"{pat}/{AUDPRE}{e0}.wav"), ffmpeg.input(f"{pat}/BG{e0}.wav")], "amix", duration = "first").output(f"{pat}/MUSIC{e0}.wav")).run()
                    return "MUSIC"
            except Exception as ex:
                fixPrint("music error.", ex)
                #printEx(ex)
                return AUDPRE
        def sfx(SOXCMD, AUDPRE):
            if len(SOXCMD) > 0:
                exportSox(AUDPRE, "SFX")
                AUDPRE = "SFX"
            d['sfx'] = constrain(int(d['sfx']), 1, 100)
            addSounds(f"{pat}/{AUDPRE}{e0}.wav", d['sfx'], f"{parentPath}/sounds")
            return AUDPRE

        audBind = {
            'threshold': threshold,
            'bass'     : bass,
            'earrape'  : earrape,
            'pitch'    : pitch,
            'reverb'   : reverb,
            'crush'    : crush,
            'wobble'   : wobble,
            'music'    : music,
            'sfx'      : sfx,
            'mute'     : mute
        }

        timer()
        SOXCMD = []
        AUDPRE = ""

        for i in orderedAudioFX:
            AUDPRE = audBind[i](SOXCMD, AUDPRE)
        timer("Audio FX")
        
        if len(SOXCMD) > 0:
            exportSox(AUDPRE, "FINAL_AUD")
            AUDPRE = "FINAL_AUD"

        audio = ffmpeg.input(f"{pat}/{AUDPRE}{e0}.wav")

    if int(width + height) > 800 or int(width) % 2 != 0 or int(height) % 2 != 0:
        split = video.split()
        video = split[0].filter("scale", "2*ceil(trunc(iw*480/ih)/2)", "480")
    video = video.filter("scale", w = "iw + mod(iw, 2)", h = "ih + mod(ih, 2)")

    s = applyBitrate('_', VBR = d['vbr'], ABR = d['abr'], **{'preset': 'veryfast'})

    if notNone(d['fisheye']):
        s = s.global_args('-aspect', f"{width}:{height}")

    TMP = ffmpeg.overwrite_output(s)
    
    if not HIDE_FFMPEG_OUT:
        fixPrint(TMP.compile()) #Use this to debug FFMPEG stuff
    timer()
    TMP.run()
    timer("Video FX")

    remove(newName)
    rename(f"{pat}/_{e0}.mp4", newName)

    customFilters = ['shuffle', 'stutter', 'ytp', 'datamosh', 'ricecake', 'clonemosh']
    customFilters = sorted(filter(lambda x: notNone(d[x]), customFilters), key=getOrder)

    def FXshuffle():
        nonlocal newName, hasAudio, DURATION, d
        stutterInputProcess(newName, '', hasAudio, entireShuffle = True, dur = DURATION)
    def FXstutter():
        nonlocal newName, hasAudio, DURATION, d
        stutterInputProcess(newName, str(d['stutter']), hasAudio, dur = DURATION)
    def FXytp():
        nonlocal newName, hasAudio, DURATION, d
        d['ytp'] = ceil(constrain(d['ytp'], 0, 100) / 10 * (float(DURATION) / 8))
        ytp(newName, int(d['ytp']), hasAudio)
    def FXdatamosh():
        nonlocal newName, d
        d['datamosh'] = constrain(d['datamosh'], 3, 100)
        if d['datamosh'] > 4:
            kint = int(100 - d['datamosh'] / 1.25)
            system(f'''ffmpeg -y -hide_banner -loglevel fatal -i '{newName}' -vcodec libx264 -x264-params keyint={kint} -max_muxing_queue_size 1024 '{pat}/1_{e0}.avi' ''')
        else:
            system(f'''ffmpeg -y -hide_banner -loglevel fatal -i '{newName}' -vcodec libx264 -max_muxing_queue_size 1024 '{pat}/1_{e0}.avi' ''')
        remove(newName)
        silent_run(["datamosh", "-o", f"{pat}/2_{e0}.avi", f"{pat}/1_{e0}.avi"])
        system(f'''ffmpeg -hide_banner -loglevel fatal -i '{pat}/2_{e0}.avi' '{pat}/3_{e0}.mp4' ''')
        remove(f"{pat}/2_{e0}.avi")
        rename(f"{pat}/3_{e0}.mp4", newName)
    def FXricecake():
        nonlocal newName, hasAudio, DURATION, d
        d['ricecake'] = max(1, max(float(DURATION) / 15, 0.25) * max(1, int(constrain(int(d['ricecake']), 1, 100) / 10)))
        ricecake(newName, d['ricecake'], hasAudio)
    def FXclonemosh():
        nonlocal hasAudio, DURATION, d, e
        d['clonemosh'] = max(1, int(constrain(int(d['clonemosh']), 1, 100) / 10))
        cloneMoshArgs = ["ruby", f"{parentPath}/clonemosh.rb", f"{pat}/{e0}", str(d['clonemosh'])]
        if notNone(d['datamosh']):
            cloneMoshArgs.append("1")
        silent_run(cloneMoshArgs, timeout = 600)

    customFilterBind = {
        'shuffle': FXshuffle,
        'stutter': FXstutter,
        'ytp': FXytp,
        'datamosh': FXdatamosh,
        'ricecake': FXricecake,
        'clonemosh': FXclonemosh
    }
    timer()
    for i in customFilters:
        customFilterBind[i]()
    timer("Custom filter time:")

    if notNone(d['selection']):
        newOut = ffmpeg.input(newName)
        aAmount = 1 if hasAudio else 0
        before, after = [], []
        SW, SH = None, None
        if ST and d['delfirst'] is None:
            start = ffmpeg.input(f"{pat}/START_{e0}.mp4")
            before = [start.video.filter("fps", fps = 30), start.audio]
            if SW is None:
                SW, SH = getSize(f"{pat}/START_{e0}.mp4")
        if ET and d['dellast' ] is None:
            end = ffmpeg.input(f"{pat}/END_{e0}.mp4")
            after = [end.video.filter("fps", fps = 30), end.audio]
            if SW is None:
                SW, SH = getSize(f"{pat}/END_{e0}.mp4")
        if SW is not None:
            newOutVideo = newOut.filter("scale", w = SW, h = SH).filter("fps", fps = 30)
            newOut = ffmpeg.concat(*(before + [newOutVideo, newOut.audio] + after), 
                n = bool(ST) + bool(ET), v = 1, a = aAmount)
            newOut = qui(newOut.output(f"{pat}/NEW_{e0}.mp4"))
            newOut.run()
            remove(newName)
            rename(f"{pat}/NEW_{e0}.mp4", newName)

    if notNone(d['timecode']) and not disallowTimecodeBreak:
        d['timecode'] = int(constrain(d['timecode'], 1, 4))
        timecodeBreak(newName, d['timecode'])


    if (isImage := (oldFormat in imageArray and not toVideo)):
        properFileName = e[0] + ".png"
        system(f'''ffmpeg -y -hide_banner -loglevel fatal -i '{newName}' -ss 0 -vframes 1 '{properFileName}' ''')
        remove(newName)
        newExt = "png"
    else:
        properFileName = e[0] + ".mp4"
        newExt = "mp4"
    
    if toGif and not isImage:
        properFileName = e[0] + ".gif"
        newExt = "gif"
        qui(
            ffmpeg.filter(
                [ffmpeg.input(newName), ffmpeg.input(newName).filter("palettegen")],
                filter_name="paletteuse"
            ).filter("fps", fps = 15).output(e[0] + ".gif", loop = 60000)
        ).run()
        remove(newName)


    return newExt

V, S = float, str

def videoEdit(properFileName, args, disallowTimecodeBreak = False, keepExtraFiles = False, SHOWTIMER = False, HIDE_FFMPEG_OUT = True, HIDE_ALL_FFMPEG = True, fixPrint = fixPrint, durationUnder = None, allowRandom = True):
    par = {
        "vbr"           :[V, round(r(0, 100))    , "vbr"],
        "abr"           :[V, round(r(0, 100))    , "abr"],
        "earrape"       :[V, round(r(0, 100))    , "er"],
        "deepfry"       :[V, round(r(0, 100))    , "df"],
        "speed"         :[V, r(-4, 4)            , "sp"],
        "timecode"      :[V, None                , "timc"],
        "bass"          :[V, round(r(0, 100))    , "bs"],
        "shuffle"       :[V, None                , "sh"],
        "toptext"       :[S, str(r(0, 100))      , "tt"],
        "bottomtext"    :[S, str(r(0, 100))      , "bt"],
        "wscale"        :[S, int(r(-500, 500))   , "ws"],
        "hscale"        :[S, int(r(-500, 500))   , "hs"],
        "topcaption"    :[S, str(r(0, 100))      , "tc"],
        "bottomcaption" :[S, str(r(0, 100))      , "bc"],
        "threshold"     :[V, None                , "thh"],
        "hue"           :[V, round(r(0, 100))    , "hue"],
        "hcycle"        :[V, round(r(0, 100))    , "huec"],
        "hypercam"      :[V, 1                   , "hypc"],
        "bandicam"      :[V, 1                   , "bndc"],
        "normalcaption" :[S, str(r(0, 100))      , "nc"],
        "cap"           :[S, str(r(0, 100))      , "cap"],
        "reverse"       :[V, 1                   , "rev"],
        "playreverse"   :[V, int(r(1, 3))        , "prev"],
        "datamosh"      :[V, int(r(0, 100))      , "dm"],
        "stutter"       :[S, int(r(0, 25))       , "st"],
        "ytp"           :[V, int(r(1, 2))        , "ytp"],
        "fisheye"       :[V, int(r(1, 2))        , "fe"],
        "clonemosh"     :[V, None                , "cm"],
        "mute"          :[V, None                , "mt"],
        "pitch"         :[V, int(r(-100, 100))   , "pch"],
        "reverb"        :[V, int(r(0, 100))      , "rv"],
        "reverbdelay"   :[V, int(r(0, 100))      , "rvd"],
        "hmirror"       :[V, 1                   , "hm"],
        "vmirror"       :[V, 1                   , "vm"],
        "ricecake"      :[V, int(r(1, 25))       , "rc"],
        "sfx"           :[V, int(r(1, 100))      , "sfx"],
        "music"         :[S, None                , "mus"],
        "musicskip"     :[V, None                , "muss"],
        "musicdelay"    :[V, None                , "musd"],
        "volume"        :[V, r(0.5, 3)           , "vol"],
        "start"         :[V, None                , "s"],
        "end"           :[V, None                , "e"],
        "selection"     :[V, None                , "se"],
        "holdframe"     :[V, None                , "hf"],
        "delfirst"      :[V, None                , "delf"],
        "dellast"       :[V, None                , "dell"],
        "shake"         :[V, int(r(1, 100))      , "shk"],
        "crush"         :[V, int(r(1, 100))      , "cr"],
        "lag"           :[V, int(r(1, 100))      , "lag"],
        "rlag"          :[V, int(r(1, 100))      , "rlag"],
        "wobble"        :[V, int(r(1, 100))      , "wub"],
        "zoom"          :[V, int(r(1, 5))        , "zm"],
        "sharpen"       :[V, int(r(-100, 100))   , "shp"],
        "watermark"     :[V, int(r(0, 100))      , "wtm"],
        "framerate"     :[V, int(r(5, 20))       , "fps"],
        "invert"        :[V, 1                   , "inv"],
        "wave"          :[V, r(-100, 100)        , "wav"],
        "waveamount"    :[V, r(0, 100)           , "wava"],
        "wavestrength"  :[V, r(0, 100)           , "wavs"]
    }

    kwargs = {}
    if 'tovid' in args.lower():
        kwargs['toVideo'] = 10
    if 'togif' in args.lower():
        kwargs['toGif'] = 10

    args = phraseArgs(args, par)

    randomSel = ''
    if len(args) == 0 or len(args[0]) == 0 and len(kwargs) == 0:
        if allowRandom:
            args = [[{'name': v, 'value': (float(par[v][1]) if par[v][0] == V else str(par[v][1])), 'order': i} for i, v in enumerate(par) if (notNone(par[v][1]) and r(0, 7) < 0.4)]]
            randomSel = " (Randomly selected)"
        else:
            return -1

    if durationUnder and getExt(properFileName) in ["mp4", "avi", "webm", "mov"]:
        if not checkIfDurationIsUnderTime(properFileName, durationUnder):
            return [1, "The video is too long to process."]

    fixPrint(f"Args{randomSel}: {strArgs(args)}")

    success = False
    newExt = None
    try:
        if not path.isdir(f"{parentPath}/active"): 
            makedirs(f"{parentPath}/active")
        newPath = f"{parentPath}/active/{getName(properFileName)}"
        if path.isdir(newPath):
            rmtree(newPath)
        makedirs(newPath)
        newFileName = f"{getName(properFileName)}.{getExt(properFileName)}"
        rename(f"{properFileName}", f"{newPath}/{newFileName}")

        #chdir(f"{newPath}") #NOTE
        
        newExt = getExt(properFileName)
        for i, group in enumerate(args):
            oldFileName = chExt(newFileName, newExt)
            newFileName = chName(properFileName, f"{i}_{chExt(properFileName, newExt)}") #f"{i}_{chExt(properFileName, newExt)}"
            rename(f"{newPath}/{oldFileName}", f"{newPath}/{newFileName}")
            newExt = destroy(f"{newPath}/{newFileName}", group, par, newExt = newExt, groupNumber = i, SHOWTIMER = SHOWTIMER, HIDE_FFMPEG_OUT = HIDE_FFMPEG_OUT, HIDE_ALL_FFMPEG = HIDE_ALL_FFMPEG, disallowTimecodeBreak = disallowTimecodeBreak, parentPath = parentPath, fixPrint = fixPrint, **kwargs)
        
        #chdir(parentPath) #NOTE
        rename(f"{newPath}/{chExt(newFileName, newExt)}", f"{parentPath}/{chExt(properFileName, newExt)}")
        removeGarbage(f"{newPath}", keepExtraFiles)
        success = True
    except Exception as ex:
        fixPrint(f'Destroyer error!')
        fixPrint("Args were:", strArgs(args))
        printEx(ex)

    if SHOWTIMER:
        print(f"Destroyer time: {time() - start_time}")

    chdir(parentPath)

    if success:
        return [0]
    else:
        fixPrint("Destroyer ran into an error.")
        tryToDelete(properFileName)
        removeGarbage(f"{newPath}", keepExtraFiles)
        return [1]

if __name__ == "__main__":
    if len(sys.argv) == 1:
        args = ""
        properFileName = "input.mp4"
    elif len(sys.argv) > 2:
        args = sys.argv[1]
        properFileName = sys.argv[2]
    if not path.isfile(properFileName):
        fixPrint("Error! Cannot find input file.")
        sys.exit(1)

    v = videoEdit(properFileName, args, disallowTimecodeBreak = len(sys.argv) != 3)
    sys.exit(v[0])