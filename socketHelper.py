import pickle, socket

def sendWithHeader(data, s):
    s.sendall(pickle.dumps(str(len(data)).rjust(10, '0'))) #25 byte header
    s.sendall(data)

def SWHAP(data, s):
    sendWithHeader(pickle.dumps(data), s)

def receiveWithHeader(s):
    head = None
    try:
        head = s.recv(25)
        if head: return pickle.loads(s.recv(int(pickle.loads(head))))
    except Exception as e:
        print("Getting data error: ", e, '-', head)
        return -1
    return False