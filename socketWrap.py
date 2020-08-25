import sys, time, socket, threading, subprocess


HOST = "70.178.231.15"
PORT = 8080
ID = sys.argv[2]
process = sys.argv[1]


def tryConn():
    s.connect((HOST, PORT))

canCom = 0
s = socket.socket()
s.settimeout(1)

def tryConn():
    global s
    try:
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
            canCom = 5

def threadMsg(msg):
    t = threading.Thread(target = sendMsg, args = (msg, ))
    t.start()

def send(msg):
    global canCom, s

    if canCom < 1:
        threadMsg(msg)
    else:
        canCom -= 1

proc = subprocess.Popen(process.split(' '), stdout = subprocess.PIPE, universal_newlines = True, shell = True)
while proc.poll() is None:
    out = proc.stdout.readline().strip()
    print(out)
    if out != "":
        send((ID + '～' + out).encode('utf-8'))
print(proc.poll)
s.close()