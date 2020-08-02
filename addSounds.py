import os
from random import randrange as r, uniform as u
from pydub import AudioSegment as AS

def getSound(sounds, i, path):
	if type(sounds[i]) == str:
		sounds[i] = AS.from_wav(f"{path}/{sounds[i]}")
	return sounds[i]
def randomSound(sounds, path):
	return getSound(sounds, r(len(sounds)), path)

def addSounds(name, amount, soundPath):
	base = AS.from_wav(name)
	sounds = list(os.listdir(soundPath))
	
	length = len(base) / 1000
	amount = max(1, int(amount * length / 60))
	intv = length / amount
	t, i = 0, 0
	while i < amount:
		t = u(t, t + 2 * intv) % length
		sfx = randomSound(sounds, soundPath)
		pos = int(t * 1000)
		if r(7) == 2:
			repeats = r(4) + 1
			for o in range(repeats):
				base = base.overlay(sfx, position = pos + o * 1250)
				t += 1
		else:
			base = base.overlay(sfx, position = pos)
		i += 1

	base.export(f"SFX{name}", format = "wav")
	os.remove(name)
	os.rename(f"SFX{name}", name)