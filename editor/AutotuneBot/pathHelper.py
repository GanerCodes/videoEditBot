import re
from os import path, remove
from shutil import rmtree

cleanRgx = re.compile(r'[\\,\/]{1,}')

def absPath(file):
    return path.abspath(file)
def getName(file):
    return path.splitext(path.split(file)[1])[0]
def getExt(file):
    return path.splitext(file)[1][1:]
def chExt(file, ext):
    return f"{path.splitext(file)[0]}.{ext}"
def getDir(file):
    return path.split(file)[0]
def chName(file, newName):
    return f"{getDir(file)}/{newName}"
def addPrefix(file, pre):
    return f"{getDir(file)}/{pre}{getName(file)}"
def chNameKeepExt(file, newName):
    return f"{getdir(file)}/{getName(newName)}.{getExt(file)}"
def cleanPath(path):
	return cleanRgx.sub('/', path)
def tryToDeleteFile(file):
    if path.isfile(file): remove(file)
def tryToDeleteDir(dr):
    if path.isdir(dr): rmtree(dr)