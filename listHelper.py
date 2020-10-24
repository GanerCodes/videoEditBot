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