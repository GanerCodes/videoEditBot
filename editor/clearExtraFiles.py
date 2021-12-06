from pathHelper import * 
import os
for i in os.listdir():
	if getExt(i) in ["mp4", "png", "jpg", "jpeg", "webm", "gif", "wmv", "bmp", "mov", "part", "wav"]:
		try:
			os.remove(i)
			print(i)
		except:
			pass