import threading, socket, pickle, random, time
from socketHelper import *

priorityList = [
    {'ID': 'dangered', 'chance': 70},
    {'ID': 'ganerserver', 'chance': 30}, 
    {'ID': 'thethirdone', 'chance': 30}
]

clientList = []

def getIndexByID(ID):
    global clientList
    for i, v in enumerate(clientList):
        if v[0] == ID: return i
    return False

def removeFromClientList(ID):
    global clientList
    if type(index := getIndexByID(ID)) == int:
        j = clientList.pop(index)
        try:
            j[1].close()
        except:
            pass
        return j
    else:
        return False

def clientHandler(conn, addr, token = None):
    global clientList
    ID = None

    SWHAP({'GET_ID': True, 'token': token}, conn)

    while True:
        if (t := receiveWithHeader(conn)) and t != -1:
            if type(t) == str: 
                if t == 'p': 
                    continue
                else:
                    print("Got a string", t)
                    continue
            elif t['type'] == "ID" and not type(getIndexByID(ID := t['ID'].lower())) == int:
                clientList.append([ID, conn, False])
                print("Added", ID, "to client list. Awaiting ready conformation.")
            elif t['type'] == "ready" and not clientList[getIndexByID(ID)][2]:
                clientList[getIndexByID(ID)][2] = True
                print(ID, "is ready for editing.")
            elif t['type'] == "file":
                print("Got file size size:", len(t['file']))
            elif t['type'] == "message":
                print(ID, "says:", t['text'])
        else:
            if removed := removeFromClientList(ID):
                print("Removed", removed[0], "from clients.")
            else:
                print("Got an invalid connection from:", addr)
            return

def addVideoProcessor(data, ID = None):
    global clientList
    if len(clientList) > 0:
        random.shuffle(priorityList)
        newList = [i for i in priorityList if i['ID'] in [o[0] for o in clientList if o[2]]]
        if len(newList) > 0:
            if ID: #If explicit
                if type(connectionIndex := getIndexByID(ID)) == int:
                    try:
                        SWHAP(data, clientList[connectionIndex][1])
                        return True
                    except:
                        removeFromClientList(ID)
                        print("Explicit ID", ID, "couldn't be reached.")
                        addVideoProcessor(data, ID)
                else:
                    print("Specific client", ID, "could not be reached.")
                    return False
            else: #If implicit
                while True:
                    for i in newList:
                        if random.randrange(100) < i['chance'] and type(connectionIndex := getIndexByID(i['ID'])) == int:
                            try:
                                SWHAP(data, clientList[connectionIndex][1])
                                return True
                            except:
                                removeFromClientList(i['ID'])
                                print("Implicit ID", i['ID'], "could not be reached.")
                                addVideoProcessor(data, ID)

        else:
            print("Couldn't find an available client.")
            return False
    else:
        print("Couldn't find an available client.")
        return False

def clientConnector(token = None):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 6444))
    while True:
        s.listen()
        conn, addr = s.accept()
        threading.Thread(target = clientHandler, args = [conn, addr, token]).start()

def strClientList():
    return ', '.join([i[0]+f" [{'✔' if i[2] else '❌'}]" for i in clientList])

def getIDList():
    return [i[0] for i in clientList if i[2]]

def getClientListLength():
    return len(clientList)

def startClientConnector(token = None):
    threading.Thread(target = clientConnector, args = [token]).start()
    print("Started client communication thread.")

if __name__ == "__main__":
    startClientConnector()