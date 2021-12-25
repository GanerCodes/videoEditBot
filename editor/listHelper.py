non_iterable = [str, int, float, type(None)]
def unwrap(x, r = None):
    if r == None: r = []
    if type(x) in non_iterable: r += [x]
    else:
        for i in x: r += unwrap(i)
    return r
    
def listReplace(ls, e1, e2):
    for i, v in enumerate(ls):
        if v == e1:
            ls[i] = e2
    return ls

def removeNone(ls):
    return list(filter(None, ls))

def trySplitBy(string, keys, times = -1):
    for i in keys:
        if i in string:
            return string.split(i, times)
    return [string]

def splitComplex(text, vals, count = -1):
    if type(vals) == str: vals = [vals]
    for i in [[text.index(p) if p in text else None for p in o] for o in vals]:
        if len(m := list(filter(lambda x: type(x) == int, i))) > 0:
            return text.split(text[min(m)], count)
    return [text]

def removeFirstPrefix(txt, pre):
    if type(pre) == str:
        pre = [pre]
    for i in pre:
        if txt.startswith(i):
            return txt.removeprefix(i)
    return txt

def startWithAny(txt, starts):
    if type(starts) == str:
        starts = [starts]
    for i in starts:
        if txt.startswith(i):
            return True
    return False

def SWRE(txt, starts, val):
    if startWithAny(txt, starts): 
        return removeFirstPrefix(txt, starts).strip() == val
    else:
        return False