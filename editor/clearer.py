import time, platform, os

def creation_date(path_to_file):
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            return stat.st_mtime

def explore(now = None, path = None):
    for i in os.listdir(t:=os.path.abspath(path)):
        i = os.path.abspath(t+'/'+i)
        if os.path.isdir(i):
            try:
                explore(now, i)
            except Exception as e:
                pass
        else:
            try:
                tt = (now - creation_date(i)) / (60 ** 2 * 24)
                if tt > 10 and "@files" not in i:
                    print(str(tt)[:12].ljust(12), os.path.split(i)[1])
                    os.remove(i)
            except Exception as e:
                print(e)
                pass

explore(time.time(), "V:")