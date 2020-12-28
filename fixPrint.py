from sys import stdout
from getSens import getSens

def fixPrint(*objects, p = print, **kwargs):
	if getSens('silent')[0].strip().lower() != "true":
	    enc = stdout.encoding
	    f = lambda obj: str(obj).encode(enc, errors='replace').decode(enc)
	    p(*map(f, objects), **kwargs)