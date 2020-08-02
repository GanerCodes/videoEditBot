import os, sys, ffmpeg, shutil, requests, subprocess, traceback, youtube_dl, time, random, math, re
from PIL        import Image
from subprocess import DEVNULL, STDOUT, check_call
from colorama   import Fore, Back, Style 
from random     import randrange

from betterStutter import stutterInputProcess
from downloadYT import downloadYT
from addSounds  import addSounds
from ricecake   import ricecake 
from ytp        import ytp
    
keepExtraFiles = False
HIDE_FFMPEG_OUT = True
parentPath = os.path.abspath('')

def r(r1, r2):
    return random.uniform(r1, r2)

def str_int(n):
    return int(float(n))

def silent_run(command, **kawrgs):
    try:
        check_call(command, stdout = DEVNULL, stderr = STDOUT, **kawrgs)
    except Exception as e:
        print(f"Silent_run error:\n", e, command)

def loud_run(command, timeout = None):
    if timeout == None:
        check_call(command)
    else:
        check_call(command, timeout = timeout)

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

def getImageRes(path):
    return Image.open(path).size

def tryToDelete(file):
    if os.path.isfile(file):
        os.remove(file)

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
    if os.path.isdir(dr):
        shutil.rmtree(dr)

def removeGarbage(path):
    if keepExtraFiles:
        return
    tryToDeleteDir(path)

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

def destroy(file, d):
    global newExt, disallowTimecodeBreak, parentPath
    properFileName = file
    currentPath = os.path.abspath('')

    def getDur(filename):
        return subprocess.getoutput(f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {filename}")

    def getSize(filename):
        return [i.strip() for i in subprocess.getoutput(f"ffprobe -v error -show_entries stream=width,height -of csv=p=0:s=x {filename}").split('x')]

    e = os.path.splitext(file)

    ST, ET = None, None

    oldFormat = e[1]
    imageArray = [".png", ".jpg", ".jpeg"]
    if e[1] in imageArray:
        os.system(f'''ffmpeg -hide_banner -loglevel fatal -framerate 1 -i {file} -c:v libx264 -r 2 -vf scale=w=ceil((iw)/2)*2:h=ceil((ih)/2)*2 -max_muxing_queue_size 1024 {e[0]}.mp4''')
        os.remove(file)
        file = e[0]+".mp4"
        e = os.path.splitext(file)
        d['datamosh'] = None
        d['hcycle'] = None
        d['stutter'] = None
        d['ytp'] = None
        d['clonemosh'] = None
        d['ricecake'] = None
        d['sfx'] = None
        d['trim'] = None
    elif e[1] != ".mp4" or notNone(d['start']) or notNone(d['end']):
        startText, endText = "", ""
        if notNone(d['start']):
            d['start'] = constrain(float(d['start']), 0, 30000) + 3.5 / 30
            ST = d['start']
            startText = f"-ss {ST} "
        if notNone(d['end']):
            d['end'] =   constrain(float(d['end'  ]), 0, 30000)
            ET = d['end']
            endText = f"-to {max(0.1, d['end'])} "
        os.system(f"ffmpeg -hide_banner -loglevel fatal -i {e[0]}{e[1]} {startText}{endText}-reset_timestamps 1 -break_non_keyframes 1 -max_muxing_queue_size 1024 -preset veryfast RFM{e[0]}.mp4")
        if notNone(d['selection']):
            if ST:
                os.system(f"ffmpeg -hide_banner -loglevel fatal -i {e[0]}{e[1]} -t {ST} -reset_timestamps 1 -break_non_keyframes 1 -max_muxing_queue_size 1024 -preset veryfast START_{e[0]}.mp4")
            if ET:
                os.system(f"ffmpeg -hide_banner -loglevel fatal -i {e[0]}{e[1]} -ss {ET} -reset_timestamps 1 -break_non_keyframes 1 -max_muxing_queue_size 1024 -preset veryfast END_{e[0]}.mp4")

        os.remove(file)
        file = e[0]+".mp4"
        os.rename(f"RFM{e[0]}.mp4", file)
        e = os.path.splitext(file)

    newName = e[0]+".mp4"
    DURATION = getDur(newName)
    hhh = subprocess.getoutput(f"ffprobe -v error -of flat=s_ -select_streams 1 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 {newName}")
    width, height = getSize(newName)
    
    vidHasAudio = True
    hasAudio = True
    audio = None

    def makeAudio(pre, dr):
        silent_run(f"sox -n -r 16000 -c 1 {pre}{e[0]}.wav trim 0.0 {dr}", timeout = 15)

    if notNone(d['holdframe']):
        d['holdframe'] = constrain(d['holdframe'], 0.1, 12)
        os.system(f"ffmpeg -hide_banner -loglevel fatal -i {newName} -frames:v 1 FIRST_FRAME_{e[0]}.png")
        video = ffmpeg.input(f"FIRST_FRAME_{e[0]}.png", loop = 1, t = d['holdframe'])
        DURATION = d['holdframe']
    
    if notNone(d['mute']) or hhh == "null" or hhh.strip() == "" or "no streams" in hhh:
        vidHasAudio = False

    if not vidHasAudio:
        if notNone(d['sfx']) or notNone(d['music']):
            makeAudio("GEN", DURATION)
            audio = ffmpeg.input(f"GEN{e[0]}.wav")
            hasAudio = True
        else:
            hasAudio = False
            d['pitch'] = None
            d['earrape'] = None
            d['abr'] = None
            d['bass'] = None
            d['threshold'] = None
            d['volume'] = None
    else:
        if notNone(d['holdframe']):
            makeAudio("HFA", d['holdframe'])
            audio = ffmpeg.input(f"HFA{e[0]}.wav")

    s = ffmpeg.input(file)
    if notNone(d['holdframe']):
        if d['mute'] is None:
            audio = ffmpeg.filter([audio, s.audio], "amix")
            hasAudio = True
    else:
        video = s.video
        if vidHasAudio:
            audio = s.audio
            hasAudio = True
        
    if notNone(d['volume']):
        d['volume'] = constrain(d['volume'], 0, 2000)
        audio = audio.filter("volume", d['volume'])

    if notNone(d['music']):
        try:
            if notNone(d['musicdelay']):
                d['musicdelay'] = constrain(d['musicdelay'], 0, DURATION)
            if downloadYT(e[0], d['music'], d['musicskip'], d['musicdelay']):
                musicMusic = ffmpeg.input(f"BG{e[0]}.wav")
                audio = ffmpeg.filter([audio, musicMusic], "amix", duration = "shortest")
        except Exception as ex:
            print("music error, "+str(ex))

    def qui(t):
        t = t.global_args("-hide_banner")
        if HIDE_FFMPEG_OUT:
            return t.global_args('-loglevel', 'fatal')
        else:
            return t

    def applyBitrate(pre, VBR = None, ABR = None, **exArgs):
        if notNone(VBR):
            exArgs.update(video_bitrate = str(VBR))
        if notNone(d['abr']):
            exArgs.update(audio_bitrate = str(ABR))
        if hasAudio:
            return qui(ffmpeg.output(video, audio, f"{pre}{newName}", **exArgs))
        else:
            return qui(ffmpeg.output(video       , f"{pre}{newName}", **exArgs))

    if notNone(d['playreverse']):
        VS = video.split()
        video = VS[0]
        newVideo = VS[1].filter("reverse")
        if d['playreverse'] == 2:
            video = ffmpeg.concat(newVideo, video)
        else:
            video = ffmpeg.concat(video, newVideo)
        if hasAudio:
            AS = audio.asplit()
            audio = AS[0]
            newAudio = AS[1].filter("areverse")
            if d['playreverse'] == 2:
                audio = ffmpeg.concat(newAudio, audio, v = 0, a = 1)
            else:
                audio = ffmpeg.concat(audio, newAudio, v = 0, a = 1)
    
    video = video.filter("scale", w = f"ceil((iw)/2)*2", h = f"ceil((ih)/2)*2")
    
    if notNone(d['abr']):
        d['abr'] = 100 + 1000 * constrain(100 - d['abr'], 1, 100)

    if notNone(d['vbr']):
        d['vbr'] = 100 + 2000 * constrain(100 - d['vbr'], 2, 100)

    if notNone(d['hmirror']):
        v2 = video.split()
        if str_int(d['hmirror']) == 2:
            flip = v2[1].filter("crop", x = "in_w/2", out_w = "in_w/2").filter("hflip")
            video = v2[0].overlay(flip)
        else:
            flip = v2[1].filter("crop", x = 0, out_w = "in_w/2").filter("hflip")
            video = v2[0].overlay(flip, x = "main_w/2")
    if notNone(d['vmirror']):
        v2 = video.split()
        if str_int(d['vmirror']) == 2:
            flip = v2[1].filter("crop", y = "in_h/2", out_h = "in_h/2").filter("vflip")
            video = v2[0].overlay(flip)
        else:
            flip = v2[1].filter("crop", y = 0, out_h = "in_h/2").filter("vflip")
            video = v2[0].overlay(flip, y = "main_h/2")

    if notNone(d['fisheye']):
        d['fisheye'] = int(constrain(d['fisheye'], 1, 2))
        for i in range(d['fisheye']):
            video = video.filter("v360" , input = "equirect", output = "ball")
            video = video.filter("scale", w = width, h = height)
        video = video.filter("setsar", r = 1)
    
    if notNone(d['bottomtext']) or notNone(d['toptext']):
        if d['bottomtext'] is None: d['bottomtext'] = "  "
        if d['toptext'   ] is None: d['toptext'   ] = "  "
        silent_run([
            "processing-java", f"--sketch={parentPath}\\impactCap", "--force", "--run",
            f"{currentPath}\\BT{e[0]}.png",
            f"{d['toptext']}", f"{d['bottomtext']}",
            f"{int(width)}", f"{int(height)}"
        ], timeout = 15)
        video = video.overlay(ffmpeg.input(f"BT{e[0]}.png"))

    if notNone(d['topcaption']) or notNone(d['bottomcaption']):
        if d['bottomcaption'] is None: d['bottomcaption'] = "  "
        if d['topcaption'   ] is None: d['topcaption'   ] = "  "
        BW, BH = float(width), float(height)
        BW, BH = BW, BH
        fac = 1086 / BW
        BW, BH = fv(fac * BW), fv(fac * BH)
        silent_run([
            "processing-java", f"--sketch={parentPath}/caption", "--force", "--run",
            f"{currentPath}\\CAP{e[0]}.png",
            f"{d['topcaption']}", f"{d['bottomcaption']}",
            str(BH)
        ], timeout = 15)
        video = ffmpeg.input(f"CAP{e[0]}.png").overlay(video.filter("scale", w = 1087, h = BH - 3).filter("setpts", "PTS-STARTPTS"), x = 96, y = 75)
        width, height = getImageRes(f"CAP{e[0]}.png")
        width, height = lim(width, height, 1000)
        width, height = fv(width), fv(height)
        video = video.filter("scale", width, height)

    if notNone(d['normalcaption']) or notNone(d['cap']):
        captionCommandline = [
            "processing-java", f'--sketch={parentPath}\\regcap', "--force", "--run",
            str(d['normalcaption']),
            f"{currentPath}\\N{e[0]}.png",
            f"{int(width)}", f"{int(height)}", "0"
        ]

    if notNone(d['normalcaption']):
        silent_run(captionCommandline, timeout = 15)
        video = ffmpeg.input(f"N{e[0]}.png").filter("pad", h = f"(ih+{height})+mod((ih+{height}), 2)").overlay(video, y = f"(main_h-{height})")
        height = str(int(height) + getImageRes(f"N{e[0]}.png")[1])
        
    if notNone(d['cap']):
        captionCommandline[-1] = "1"
        captionCommandline[-4] = f"{currentPath}\\C{e[0]}.png"
        captionCommandline[-5] = d['cap']
        silent_run(captionCommandline, timeout = 15)
        video = ffmpeg.input(f"C{e[0]}.png").filter("pad",h=f"(ih+{height})+mod((ih+{height}), 2)").overlay(video, y = f"(main_h-{height})")
        height = str(int(height) + getImageRes(f"C{e[0]}.png")[1])

    if notNone(d['hypercam']):
        video = video.overlay(ffmpeg.input(f"{parentPath}/images/hypercam.png").filter("scale", w = width, h = height))

    if notNone(d['bandicam']):
        video = video.overlay(ffmpeg.input(f"{parentPath}/images/bandicam.png").filter("scale", w = width, h = height))

    if notNone(d['deepfry']):
        q = 2 * constrain(d['deepfry'] * 10, 0, 1000)
        if q > 1000:
            q = -q
        video = video.filter("eq", saturation = 1 + (d['deepfry'] / 100), contrast = 1 + q / 10)

    if notNone(d['hue']) or notNone(d['hcycle']):
        if d['hue'] is None:
            d['hue'] = 0
        else:
            d['hue'] = int(3.6 * constrain(d['hue'], 0, 100))
        if d['hcycle'] is None:
            d['hcycle'] = 0
        else:
            d['hcycle'] = constrain(d['hcycle'], 0, 100) / 10
        video = video.filter("hue", h = f'''{d['hue']} + ({d['hcycle']}*360*t)''')

    if notNone(d['speed']):
        if d['speed'] < 0:
            d['reverse'] = 1
        q = constrain(abs(d['speed']), 0.5, 25)
        video = video.filter("setpts", (str(1 / q)+"*PTS"))
        if hasAudio:
            audio = audio.filter("atempo", q)

    if notNone(d['reverse']):
        video = video.filter("reverse")
        if hasAudio:
            audio = audio.filter("areverse")

    if notNone(d['hscale']) or notNone(d['wscale']):
        scaleX = constrain(math.ceil(str_int(d['wscale']) / 2) * 2, -600, 600) if notNone(d['wscale']) else "iw"
        scaleY = constrain(math.ceil(str_int(d['hscale']) / 2) * 2, -600, 600) if notNone(d['hscale']) else "ih"
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
    
    if notNone(d['bass']):
        d['bass'] = constrain(d['bass'], 0, 100)
        audio = audio.filter("equalizer", f = 50, width_type = 'h', width = 50, g = d['bass'], mix = d['bass'] / 100)

    if notNone(d['threshold']):
        n = constrain(d['threshold'], 1, 100) / 3 - 20
        audio = audio.filter("compand", attacks=0, points=f'''-900/-900|{n}/-900|{n}/0''')

    if notNone(d['earrape']):
        d['earrape'] = constrain(d['earrape'] + 20, 0.1, 100)
        q = int(constrain(d['earrape'] / (100 / 24) + 48, 48, 64))
        a2 = audio.filter("acrusher", level_in = 0.1, level_out = 1, bits = q, mix = 0, mode = "log")
        qui((a2.output(f"_{e[0]}.wav").overwrite_output())).run()
        audio = ffmpeg.input(f"_{e[0]}.wav")

    if notNone(d['pitch']):
        d['pitch'] = 12 * int(constrain(d['pitch'], -100, 100))
        qui(audio.output(f"{e[0]}.wav").overwrite_output()).run()
        silent_run(["sox", f"{e[0]}.wav", f"1{e[0]}.wav", "pitch", str(d['pitch'])])
        os.remove(f"{e[0]}.wav")
        audio = ffmpeg.input(f"1{e[0]}.wav")

    if notNone(d['sfx']):
        d['sfx'] = constrain(int(d['sfx']), 1, 100)
        qui(audio.output(f"SFX{e[0]}.wav").overwrite_output()).run()
        addSounds(f"SFX{e[0]}.wav", d['sfx'], f"{parentPath}/sounds")
        audio = ffmpeg.input(f"SFX{e[0]}.wav")

    limited = {'preset': 'veryfast'}
    if d['holdframe'] and d['holdframe'] < float(DURATION):
        pass#limited['shortest'] = None
    s = applyBitrate('_', VBR = d['vbr'], ABR = d['abr'], **limited)

    if notNone(d['fisheye']):
        s = s.global_args('-aspect', f"{width}:{height}")

    TMP = ffmpeg.overwrite_output(s)
    #print(TMP.compile()) #Use this to debug FFMPEG stuff
    TMP.run()

    os.remove(newName)
    os.rename("_" + newName, newName)

    if notNone(d['shuffle']):
        stutterInputProcess(newName, '', hasAudio, entireShuffle = True, dur = DURATION)

    if notNone(d['stutter']):
        stutterInputProcess(newName, str(d['stutter']), hasAudio, dur = DURATION)

    if notNone(d['ytp']):
        d['ytp'] = math.ceil(constrain(d['ytp'], 0, 100) / 10 * (float(DURATION) / 8))
        ytp(newName, int(d['ytp']), hasAudio)

    if notNone(d['datamosh']):
        d['datamosh'] = constrain(d['datamosh'], 3, 100)
        if d['datamosh'] > 4:
            kint = int(100 - d['datamosh'] / 1.25)
            subprocess.run(f"ffmpeg -y -hide_banner -loglevel fatal -i {newName} -vcodec libx264 -x264-params keyint={kint} -max_muxing_queue_size 1024 1_{e[0]}.avi")
        else:
            subprocess.run(f"ffmpeg -y -hide_banner -loglevel fatal -i {newName} -vcodec libx264 -max_muxing_queue_size 1024 1_{e[0]}.avi")
        os.remove(newName)
        silent_run(["C:/Ruby27-x64/bin/datamosh.bat", "-o", f"2_{e[0]}.avi", f"1_{e[0]}.avi"])
        subprocess.run(f"ffmpeg -hide_banner -loglevel fatal -i 2_{e[0]}.avi 3_{e[0]}.mp4")
        os.remove(f"2_{e[0]}.avi")
        os.rename(f"3_{e[0]}.mp4", newName)

    if notNone(d['ricecake']):
        d['ricecake'] = max(1, max(float(DURATION) / 15, 0.25) * max(1, int(constrain(int(d['ricecake']), 1, 100) / 10)))
        ricecake(newName, d['ricecake'], hasAudio)

    if notNone(d['clonemosh']):
        d['clonemosh'] = max(1, int(constrain(int(d['clonemosh']), 1, 100) / 10))
        cloneMoshArgs = ["C:/Ruby27-x64/bin/ruby.exe", f"{parentPath}/clonemosh.rb", e[0], str(d['clonemosh'])]
        if notNone(d['datamosh']):
            cloneMoshArgs.append("1")
        silent_run(cloneMoshArgs, timeout = 600)

    if notNone(d['selection']):
        newOut = ffmpeg.input(newName)
        aAmount = 1 if hasAudio else 0
        before, after = [], []
        SW, SH = None, None
        if ST and d['delfirst'] is None:
            start = ffmpeg.input(f"START_{e[0]}.mp4")
            before = [start.video.filter("fps", fps = 30), start.audio]
            if SW is None:
                SW, SH = getSize(f"START_{e[0]}.mp4")
        if ET and d['dellast' ] is None:
            end = ffmpeg.input(f"END_{e[0]}.mp4")
            after = [end.video.filter("fps", fps = 30), end.audio]
            if SW is None:
                SW, SH = getSize(f"END_{e[0]}.mp4")
        if SW is not None:
            newOutVideo = newOut.filter("scale", w = SW, h = SH).filter("fps", fps = 30)
            newOut = ffmpeg.concat(*(before + [newOutVideo, newOut.audio] + after), 
                n = bool(ST) + bool(ET), v = 1, a = aAmount)
            newOut = qui(newOut.output(f"NEW_{e[0]}.mp4"))
            #print(newOut.compile())
            newOut.run()
            os.remove(newName)
            os.rename(f"NEW_{e[0]}.mp4", newName)

    if notNone(d['timecode']) and not disallowTimecodeBreak:
        d['timecode'] = int(constrain(d['timecode'], 1, 4))
        timecodeBreak(newName, d['timecode'])

    #Nope, gifs suck way too much to use, they become MP4's now.
    # if oldFormat == ".gif":
    #     properFileName = e[0] + ".gif"
    #     qui(
    #         ffmpeg.filter(
    #             [ffmpeg.input(newName), ffmpeg.input(newName).filter("palettegen")],
    #             filter_name="paletteuse"
    #         ).filter("fps", fps = 45).output(e[0] + ".gif", loop = 23874)
    #     ).run()
    #     os.remove(newName)
    elif oldFormat in imageArray:
        properFileName = e[0] + ".png"
        os.system(f'''ffmpeg -y -hide_banner -loglevel fatal -i {newName} -ss 0 -vframes 1 {properFileName}''')
        os.remove(newName)
        newExt = "png"
    else:
        properFileName = e[0] + ".mp4"
        newExt = "mp4"

if len(sys.argv) > 2:
    args = sys.argv[1]
    properFileName = sys.argv[2]

if not os.path.isfile(properFileName):
    print("Error! Cannot find input file.")
    sys.exit(1)

disallowTimecodeBreak = len(sys.argv) != 3

args = args.replace('\n', ' ')

V, S = float, str
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
    "stutter"       :[S, "50.1.1.1"          , "st"],
    "ytp"           :[V, int(r(1, 2))        , "ytp"],
    "fisheye"       :[V, int(r(1, 2))        , "fe"],
    "clonemosh"     :[V, int(r(1, 5))        , "cm"],
    "mute"          :[V, None                , "mt"],
    "pitch"         :[V, int(r(-100, 100))   , "pch"],
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
    "dellast"       :[V, None                , "dell"]
}
bind = {par[i][2]: i for i in par}

def strArgs(args):
    return '|'.join([','.join(['='.join([(str(j)) for j in o]) for o in i]) for i in args])

args = [a for group in args.split('|') if len(a:=[b for command in group.split(',') if len(b:=(((([g[0], g[1] if par[g[0]][0] == S else (float(('-' if g[1][0] == '-' else '') + d) if len(str(d:=(re.sub(r"([^0-9.])", '', g[1]).replace('.', '', max(0, (g[1]).count('.') - 1))))) > 0 else 1)]) if len(c) > 1 else [g[0], 'true' if par[g[0]][0] == S else 1.0])) if len(c) > 0 and (par[g[0]][0] == S or g[-1] != "false") else []) if len(g:=(c if ((c:=[(r.strip()) for r in (command.split('=', 1) if '=' in command else command.split(' ', 1))])[0] in par) else (([bind[c[0]], c[1]] if len(c) > 1 else [bind[c[0]]]) if (c[0] in bind) else []))) > 0 else []) > 0]) > 0][:3]
#splts by '|', splits by ',', splits by '=' if '=' is in it, otherwise split by ' ', strip those, exit those args if any of those args are 'false', make sure args[0] (the filter name) is in the filter list, if that filter value is a float, turn it into a float by removing all but the last '.'. If any of the created lists have a length of 0, don't add it (applys to all layers)

randomSel = ""
if len(args) == 0:
    randomSel = " (randomly selected)"
    args = [[]]
    for i in par:
        if r(0, 7) < 1: args[0].append([i, par[i][1]])

print(f"Args{randomSel}: {strArgs(args)}")

def getName(file):
    return os.path.splitext(file)[0]
def getExt(file):
    return os.path.splitext(file)[1][1:]
def chExt(file, ext):
    return f"{os.path.splitext(file)[0]}.{ext}"

success = False
newExt = None
try:
    splPath = os.path.splitext(properFileName)
    if not os.path.isdir("active"): os.makedirs("active")
    newPath = f"active/{splPath[0]}"
    if os.path.isdir(newPath):
        shutil.rmtree(newPath)
    os.makedirs(newPath)
    os.rename(properFileName, f"{newPath}/{properFileName}")
    os.chdir(f"{newPath}")
    newFileName = properFileName
    newExt = getExt(properFileName)
    for i, group in enumerate(args):
        oldFileName = chExt(newFileName, newExt)
        newFileName = f"{i}_{chExt(properFileName, newExt)}"
        os.rename(oldFileName, newFileName)
        destroyPar = {i: None for i in par}
        for o in group: destroyPar[o[0]] = o[1]
        destroy(newFileName, destroyPar)
    os.chdir(parentPath)
    os.rename(f"{newPath}/{chExt(newFileName, newExt)}", f"{chExt(properFileName, newExt)}")
    removeGarbage(f"{newPath}")
    success = True
except Exception as ex:
    print(f'Destroyer error! "{traceback.format_exc()}"')

print("Destroyer finished.")
if success:
    sys.exit(0)
else:
    os.chdir(parentPath)
    tryToDelete(properFileName)
    removeGarbage(f"{newPath}")
    sys.exit(1)