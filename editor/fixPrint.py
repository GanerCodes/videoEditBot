from sys import stdout

def fixPrint(*objects, p = print, **kwargs):
	enc = stdout.encoding
	f = lambda obj: str(obj).encode(enc, errors='replace').decode(enc)
	p(*map(f, objects), **kwargs)