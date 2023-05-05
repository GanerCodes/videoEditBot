from os import rename, remove, path
from download import download
from pathHelper import *
from subprocessHelper import *
import subprocess, random


loglevel = "error"

def getDur(f):
	return eval(subprocess.getoutput(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", f]))

def autotune(base, over, filename, strength = 75, executableName = "./autotune.exe", reformatAudio = True, hz = 48000):
	strength = max(1, min(strength, 512))
	if reformatAudio:
		baseDur = getDur(base)
		loud_run(["ffmpeg", "-y", "-hide_banner", "-loglevel", loglevel, "-i", base, "-ac", "1", "-ar", hz, base := chExt(addPrefix(absPath(base), 'AT_'), 'wav')])
		loud_run(["ffmpeg", "-y", "-hide_banner", "-loglevel", loglevel, "-i", over, "-ac", "1", "-ar", hz, '-t', str(baseDur), over := chExt(addPrefix(absPath(over), 'AT_'), 'wav')])
	silent_run([executableName, '-b', strength, base, over, filename])
	if reformatAudio:
		remove(base)
		remove(over)

randDigits = lambda: str(random.random()).replace('.', '') 

def autotuneURL(filename, URL, replaceOriginal = True, video = True, executableName = "./autotune.exe"):
	directory = path.split(path.abspath(filename))[0]
	downloadName = f"{directory}/download_{randDigits()}.wav"
	result = download(downloadName, URL, video = False, duration = 2 * 60)
	if result:
		wavName = f'{directory}/vidAudio_{randDigits()}.wav'
		if video:
			loud_run(["ffmpeg", "-hide_banner", "-loglevel", loglevel, "-i", filename, "-ac", "1", wavName])
		else:
			rename(filename, wavName)
		autotuneName = f'{directory}/autotune_{randDigits()}.wav'
		autotune(wavName, downloadName, autotuneName, executableName = executableName)
		remove(downloadName)
		remove(wavName)
		exportName = f"{directory}/{randDigits()}{path.splitext(filename)[1]}"
		if video:
			loud_run(["ffmpeg", "-hide_banner", "-loglevel", loglevel, "-i", filename, "-i", autotuneName, "-map", "0:v", "-map", "1:a", "-ac", "1", exportName])
			remove(autotuneName)
		else:
			rename(autotuneName, exportName)
		
		if replaceOriginal:
			if video:
				remove(filename)
			rename(exportName, filename)
			return filename
		return exportName
	else:
		return [f"Error downloading {URL}"]