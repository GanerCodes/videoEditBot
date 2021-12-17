from subprocess import run
import os
fh = bytes.fromhex

def datamosh(video1, video2, replace_input = False, has_audio = True):
    vid_tmp = f"{video1}_VID.avi"
    aud_tmp = f"{video2}_AUD.mp3"
    avi_out = f"{video1}_AVI.avi"

    run(f"""ffmpeg -y -hide_banner -loglevel fatal -i {video1} -pix_fmt yuv420p -map 0:v {vid_tmp}""")
    if has_audio:
        run(f"""ffmpeg -y -hide_banner -loglevel fatal -i {video1} -map 0:a {aud_tmp}""")
    if os.path.isfile(avi_out): os.remove(avi_out)
    with open(vid_tmp, 'rb') as oavi:
        with open(avi_out, 'wb') as iavi:
            pf = None
            for fCount, f in enumerate(spl := oavi.read().split(fd := fh("30306463"))):
                if fCount > len(f) - 3 or fCount < 3 or f[5:8] != fh("0001B0"):
                    iavi.write(f + fd)
                else:
                    iavi.write(fh("00" * len(f)) + fd)
                pf = f
                fCount += 1
    if has_audio:
        run(f"""ffmpeg -y -hide_banner -loglevel fatal -i {avi_out} -i {aud_tmp} -c:a copy -map 0:v -map 1:a {video2}""")
    else:
        run(f"""ffmpeg -y -hide_banner -loglevel fatal -i {avi_out} -c:a copy -map 0:v {video2}""")
    os.remove(aud_tmp)
    os.remove(avi_out)
    if replace_input:
        os.remove(video1)
        os.rename(video2, video1)