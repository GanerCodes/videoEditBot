def formatKey(l):
	if l.count('='):
		return l.split('=', 1)[1].strip().replace('"', '')
	else:
		return ''

def getSens(*types, filename = "TOKENS.txt"):
	types = list(types)
	result = [''] * len(types)
	with open("TOKENS.txt") as f:
		for line in f:
			l = line.lower()
			for i, v in enumerate(types): 
				v = v.lower()
				if l.strip().startswith(v):
					result[i] = formatKey(line)
					break
	return result