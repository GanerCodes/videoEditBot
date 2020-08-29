def formatKey(l):
	return l.split('=')[1].strip().replace('"', '')

def getSens(*types, filename = "TOKENS.txt"):
	types = list(types)
	with open("TOKENS.txt") as f:
		for line in f:
			l = line.lower()
			for i, v in enumerate(types):
				v = v.lower()
				if v in l:
					types[i] = formatKey(line)
					break
	return types