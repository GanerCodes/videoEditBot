import os, subprocess, sys, requests
from pathHelper import *
from PIL import Image
from random import randrange as r

# def breakImage(file):
#     t = os.path.splitext(file)
#     if t[1] == ".png":
#         im = Image.open(file)
#         rgb = im.convert('RGB')
#         rgb.save(t[0]+".jpg")
#         os.remove(file)
#         os.rename(t[0]+".jpg", file)
#     with open(file, "rb") as binaryFile:
#         b = bytearray(binaryFile.read())
#     n = max(int(len(b) / 8500), 15)
#     n2 = int(r(1, 3))
#     for i in range(n):
#         t = int(r(600, len(b) - 200))
#         for o in range(n2):
#             b[t + o] = int(r(0, 256)) 
#     new = open(file, 'wb')
#     new.write(b)

def ruin(file, fac):
    i = Image.open(file)

    pat = getDir(file)

    i = i.convert('RGB')
    w, h = i.size
    z = int((w + h) / int(fac))
    i = i.resize((max(1, z), max(1, z)), Image.NEAREST)

    nn = f"{pat}/_{getName(file)}.jpg"
    i.save(nn, "JPEG", quality = 2)
    i = Image.open(nn)

    i = i.resize((max(1, w), max(1, h)), Image.NEAREST)

    nn2 = f"{pat}/_{getName(nn)}.jpg"

    i.save(nn2, "png")
    os.remove(nn);
    os.remove(file)
    os.rename(nn2, os.path.splitext(file)[0]+".png")

def imageCorrupt(filename, destroyAmount):
    ruin(filename, destroyAmount)
    return [0]

if __name__ == "__main__":
    if len(sys.argv) < 4:
        filename = sys.argv[2]
        destroyAmount = sys.argv[1]
        ruin(filename, destroyAmount)
    else:
        url = sys.argv[1];
        req = requests.get(url, allow_redirects=True)
        open(sys.argv[2], 'wb').write(req.content)
        ruin(sys.argv[2], sys.argv[3])