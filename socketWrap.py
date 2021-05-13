import sys, time, socket, threading, subprocess
from getSens import getSens


RESTART_DELAY_TIME = 1


HOST, PORT = getSens("log_ip")[0], 8080 #IP and port you want to send logs to
process, ID = sys.argv[1], sys.argv[2]

if len(sys.argv) > 3: 
    HAS_NAME = False
else:
    HAS_NAME = True

if HAS_NAME: prefix = f"[{getSens('name')[0]}] "
else: prefix = ''

canCom = 0
s = socket.socket()

def tryConn():
    global s
    try:
        s = socket.socket()
        s.settimeout(1)
        s.connect((HOST, PORT))
        return True
    except Exception as e:
        return False

tryConn()

def sendMsg(msg):
    global canCom, s

    try:
        s.sendall(msg)
    except Exception as e:
        if tryConn():
            s.sendall(msg)
        else:
            canCom = 10

def threadMsg(msg):
    t = threading.Thread(target = sendMsg, args = (msg, ))
    t.start()

def send(msg):
    global canCom
    if    canCom < 1: threadMsg(msg)
    else: canCom -= 1

while 1:
    print("[SocketWrap] starting process.")
    proc = subprocess.Popen(process, stdout = subprocess.PIPE, universal_newlines = True, shell = True)
    while proc.poll() is None:
        out = proc.stdout.readline().strip()
        print(out)
        if out != "":
            send((ID + '～' + prefix + out).encode('utf-8'))
    s.close()
    try: proc.kill()
    except: pass
    print("[SocketWrap] Process ended. Resarting.")
    time.sleep(RESTART_DELAY_TIME)