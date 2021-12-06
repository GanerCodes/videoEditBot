import os, io, sys, time, shutil, random, discord, socket, pickle, aiohttp, asyncio, threading, subprocess, datetime, random, websockets, uuid
from PIL import Image
from math import ceil
from getSens import getSens
from fixPrint import fixPrint
from download import download
from editor import videoEdit
from threadQue import *
from listHelper import *
from imageCorrupt import imageCorrupt
Popen = subprocess.Popen
Thread = threading.Thread

MESSAGE_CHECK_AMOUNT = 10
DIRECTORY = f"{getSens('dir')[0]}/@"
BASE_URL = f"{getSens('website')[0]}/@"
DISPLAY_MESSAGES = False
MSG_DISPLAY_LEN = 75
TAGLINE = 'https://discord.com/invite/aFrEBEN'
IP_ADDR, PORT = "0.0.0.0", 6444
VERBOSE_OUTPUT = False

print("Starting Discord bot...")

TOKEN, guilds = getSens("discord", "guilds")

if not os.path.isdir(p:=f"{DIRECTORY}"):
    os.makedirs(p)
    print(f'Created directory "{p}"')

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

def formatKey(l):
    return l.split('=')[1].strip().replace('"', '')

priorityList = [
    {'name': 'ganerserver', 'chance': 100},
    # {'name': 'johnny5', 'chance': 25},
    # {'name': 'ganerserver', 'chance': 35}, 
]

clients = {}
async def videoEditBotMasterServer(w, path):
    try:
        ID = uuid.uuid4().hex
        print(f"{ID}: Connected")
        clients[ID] = {"websocket": w, "name": None, "canEdit": False, "chance": 0}
        await w.send(pickle.dumps("getName"))
        while True:
            data = await w.recv()
            try:
                data = pickle.loads(data)
                if VERBOSE_OUTPUT: fixPrint(f"{ID}: |||{data}")
                if type(data) == dict:
                    if data['type'] == 'name':
                        clients[ID]['name'] = data['name']
                        clients[ID]['chance'] = [i for i in priorityList if i['name'] == clients[ID]['name']][0]['chance']
                        print(f"{ID}: Got name: {data['name']} (Edit chance: {clients[ID]['chance']}%)")
                        await w.send(pickle.dumps({'type': 'key', 'key': TOKEN}))
                    elif data['type'] == 'ready':
                        clients[ID]['canEdit'] = True
                        print(f"{ID}: {clients[ID]['name']} ready to edit!")
            except Exception as e2:
                raise Exception("Error unpickling.", data)
    except Exception as e:
        print(f"{ID}: Disconnecting. ({clients[ID]['name']})", e)
        clients.pop(ID, None)
        await w.close()
        
        
def runServer():
    print("Starting server...")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(server)
    loop.run_forever()
async def addVideoProcessor(data, ID = None):
    global clients
    if ID == None:
        if len(newClients := {i: clients[i] for i in clients if clients[i]['canEdit']}) > 0:
            editClient = None
            while editClient == None:
                if random.random() <= (j := newClients[random.choice(list(newClients.keys()))])['chance'] / 100:
                    editClient = j
            # fixPrint("TEST|||||SENDING DATA", data)
            await editClient['websocket'].send(pickle.dumps(data))
            return True
        return False
    else:
        newSocket = [clients[i]['websocket'] for i in clients if clients[i]['name'] == ID]
        if len(newSocket) > 0:
            await newSocket[0].send(pickle.dumps(data))
            return True
        return False

threading.Thread(target = runServer).start()

def UFID(ID, l):
    random.seed(ID)
    return ''.join([str(random.randint(0,9)) for i in range(l)])

def botPrint(*o, prefix = "", **ko):
    if len(o) > 0:
        o = list(o)
        o[0] = "#\t" + str(o[0])
    fixPrint(*o, **ko)

def prettyRun(pre, cmd):
    tab, nlin = '\t', '\n'
    proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, universal_newlines = True)
    while proc.poll() is None:
        out = proc.stdout.readline()
        if out != "":
            fixPrint(f"#{tab}{pre}: {out.replace(nlin, '')}")
    return proc.returncode

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status != 200:
                return None
            else:
                return io.BytesIO(await r.read())

def trim(txt, l):
    return txt[:l] + ("…" if len(txt) > l else "")

def setLength(txt, l):
    return txt[:l - 1] + ("…" if len(txt) > l else "_" * (l - len(txt)))

timedGuilds = []
timedUsers = []

intents = discord.Intents.default()
#intents.members = True
intents.messages = True #The fact that this is now a """privilaged""" intent is stupid, Discord is literally going against their dev community in doing this shows the starting of the fall of their platform
bot = discord.AutoShardedClient(status = discord.Game(name = TAGLINE), intents = intents)
botIsReady = False

async def tryTimedCommand(user, message):
    global timedUsers, timedGuilds

    currentTime = time.time()
    if user.id != bot.user.id:

        userTier  = getTier(user.id)
        guildTier = getTier(message.guild.owner_id)

        userDelay  = (7  if userTier  == 1 else (3 if userTier  == 2 else 1)) if userTier  else False
        guildDelay = (10 if guildTier == 1 else (5 if guildTier == 2 else 1)) if guildTier else 15

        if userDelay and userDelay <= guildDelay:
            for i, v in enumerate(timedUsers):
                if v["id"] ==  user.id:
                    if v["time"] < currentTime:
                        v["time"] = currentTime + userDelay
                    else:
                        await message.channel.send(f"<@!{user}> Please wait {(seconds:=ceil(v['time'] - currentTime))} more second{'s' if seconds > 1 else ''} to use the bot again.")
                        return False
                    break
            else:
                timedUsers.append({"id": user.id, "time": currentTime + userDelay})
        else:
            for i, v in enumerate(timedGuilds):
                if v["id"] == message.guild.id:
                    if v["time"] < currentTime:
                        v["time"] = currentTime + guildDelay
                    else:
                        await message.channel.send(f"Please wait {(seconds:=ceil(v['time'] - currentTime))} more second{'s' if seconds > 1 else ''} to use the bot again.")
                        return False
                    break
            else:
                timedGuilds.append({"id": message.guild.id, "time": currentTime + guildDelay})
    return True

@bot.event
async def on_ready():
    print("ON_READY() TRIGGERED")
    if not botIsReady:
        await bot.change_presence(activity = discord.Game(name = TAGLINE))
        await updateSubscriptionList()

@bot.event
async def on_message(message):
    # print(message)
    global VERBOSE_OUTPUT

    if not botIsReady: return

    if DISPLAY_MESSAGES:
        if message.guild == None:
            fixPrint(trim(f"|\t{setLength('DMs', 10)}/{setLength(message.author.name, 10)}: {message.content}", MSG_DISPLAY_LEN))
            return
    elif message.guild == None: return

    if not message.channel.permissions_for(message.guild.me).send_messages: return

    guildID = message.guild.id

    async def post(x):
        await message.channel.send(x)

    txt = message.content
    ltxt = txt.strip().lower()
    user = message.author
    
    dil, sep = '*' if user == bot.user else '|', '\n'
    fmtTxt = f"{setLength(message.guild.name, 10)}/{setLength(message.channel.name, 10)}/{setLength(user.display_name, 10)}: {txt.strip().replace(sep,'^')}"
    if DISPLAY_MESSAGES: fixPrint(f'''{dil}\t{trim(fmtTxt, MSG_DISPLAY_LEN)}''')

    try:
        t = [len(i) for i in ["download", "downloader"] if ltxt.strip().startswith(i)]
        if len(t) > 0 and await tryTimedCommand(user, message):
            repl = '@'+chr(8206)
            t = max(t) + 1
            rgs = ' '.join(txt.strip()[t:].strip().split())
            rgs = trySplitBy(rgs, "|, ", 1)
            if len(rgs) > 1 and rgs[1].startswith("destroy"):
                rgs[1] = rgs[1][7:]
            
            replyMessage = (f"destroy {rgs[1].replace('@', repl).strip()} ║ " if (len(rgs) > 1 and len(rgs[1].strip()) > 0) else '') + f"<@{user.id}>"
            result = await addVideoProcessor({
                'type': 'download',
                'url': rgs[0],
                'guild': guildID,
                'channel': message.channel.id,
                'message': replyMessage
            })
            if not result: await message.channel.send("Sorry, we couldn't find a server to download this video. [likely the bot's being worked on currently]")

    except Exception as e:
        fixPrint(e)
        await post("This, ideally, should never be seen. However, as I am bad at programming, it can be seen. I'm most likely already working on it. Existance is pain.")

    if SWRE(ltxt, ['videoeditbot', 'veb', 'destroy'], "help"):
        await post("Command documentation: https://github.com/GanerCodes/videoEditBot/blob/master/COMMANDS.md")
        return

    if SWRE(ltxt, ['videoeditbot', 'veb'], "test"):
        print("Got test request for:", clientNameList := [clients[i]['name'] for i in clients])
        for i in clientNameList:
            await addVideoProcessor({
                'type': 'edit',
                'url': "https://i.imgur.com/5AbBR58.jpg",
                'guild': guildID,
                'channel': message.channel.id,
                'oldExt': "jpg",
                'args': f"cap {i}",
                'message': i
            }, ID = i)

    if ltxt.startswith("debug this"):
        print(ltxt)
    
    prefixLength = 0
    if ltxt.strip().startswith("destroy"):
        prefixLength = 7
    elif ltxt.strip().startswith(pref:=f"<@!{bot.user.id}>"):
        prefixLength = len(pref)
    elif ltxt.strip().startswith("videoeditbot"):
        prefixlength = 12
    if prefixLength and await tryTimedCommand(user, message):
        attach = None
        if len(message.attachments) > 0:
            attach = message.attachments[0]
        elif message.reference and len(tmpDat := (await message.channel.fetch_message(message.reference.message_id)).attachments) > 0:
            attach = tmpDat[0]
        else:
            async for msg in message.channel.history(limit = MESSAGE_CHECK_AMOUNT):
                if len(msg.attachments) > 0:
                    attach = msg.attachments[0]
                    break
        if not attach:
            await post(f"Could not find a video or image in the last {MESSAGE_CHECK_AMOUNT} messages.")
            return

        e = os.path.splitext(attach.filename)
        oldExt = e[1].lower()[1:]

        newExt = None
        isImage = oldExt in ["png", "jpg", "jpeg"]
        if "tovid" in txt.lower():
            newExt = "mp4"
        elif oldExt in ["mp4", "mov", "webm", "gif"]:
            if "togif" in txt.lower() and not isImage:
                newExt = "gif"
            else:
                newExt = "mp4"
        elif isImage:
            newExt = "png"
        else:
            await post("File format unavailable.\nFile format list: webm, mp4, mov, gif, jpg/jpeg, png")
            return

        choices = ["your autism has arrived, sire", "h", "Here ya go", "You can help support the bot and get extra perks through Patreon! (<https://www.patreon.com/videoeditbot>)", "Is this one as bad as the last one?", "هي لعبة الكترونية", "That moment when", "New punjabi movies 2014 full movie free download hd 1080p", "Yo mama moment", "Help support the bot by donating some ETH! 0x013d1361177ab72b0cf096bd34fa671efb3eeeee"]
        if guildID == 463054124766986261: choices.append("your autism, madam")

        if user == bot.user:
            mentionID = message.mentions[0].id if len(message.mentions) > 0 else ''
        else: mentionID = user.id

        args = {
            'type': 'edit',
            'url': attach.url,
            'guild': guildID,
            'channel': message.channel.id,
            'oldExt': oldExt,
            'args': txt.strip()[prefixLength:].split('║')[0],
            'message': f"{random.choice(choices)} ║ <@{mentionID}>"
        }
        if len(spl := args['args'].split('>srv>', 1)) > 1:
            args['args'] = spl[0].strip()
            result = await addVideoProcessor(args, ID = spl[1].strip())
        else:
            result = await addVideoProcessor(args)
        if not result: await message.channel.send("Sorry, we couldn't find a server to edit this video. [likely the bot's being worked on atm]")

    if ltxt == "hat":
        await message.channel.send(file = discord.File("hat.png"))
        return

    if ltxt == "verbose_veb_on":
        for i in clients: await clients[i]['websocket'].send(pickle.dumps("verbose_veb_on"))
        print("Verbose output set to:", VERBOSE_OUTPUT := True)
        return
    if ltxt == "verbose_veb_off":
        for i in clients: await clients[i]['websocket'].send(pickle.dumps("verbose_veb_off"))
        print("Verbose output set to:", VERBOSE_OUTPUT := False)
        return

    if dil == '*':
        return

    if ltxt.strip().startswith("avatar"):
        if len(message.mentions) > 0:
            await post(str(message.mentions[0].avatar_url))
            return
        elif ltxt.strip() == "avatar":
            await post(str(user.avatar_url))
            return

bot.run(TOKEN)