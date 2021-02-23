import os, io, sys, time, shutil, random, discord, socket, pickle, aiohttp, asyncio, threading, subprocess, datetime
import sqlite3 as sql
from PIL import Image
from math import ceil
from getSens import getSens
from fixPrint import fixPrint
from download import download
from destroyer import videoEdit
from threadQue import *
from listHelper import *
from masterNode import *
from imageCorrupt import imageCorrupt
Popen = subprocess.Popen
Thread = threading.Thread

MESSAGE_CHECK_AMOUNT = 10
DIRECTORY = f"{getSens('dir')[0]}/@"  #/mnt/hgfs/VideoEditBot/Twitter/@"
BASE_URL = f"{getSens('website')[0]}/@"
DISPLAY_MESSAGES = False
MSG_DISPLAY_LEN = 75
TAGLINE = 'https://discord.gg/aFrEBEN'  #"twitter.com/VideoEditBot"
CHECK_PATREON = True

print("Starting Discord bot...")

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

TOKEN, guilds = getSens("discord", "guilds")
patreonServerID = int(getSens("patreon_server")[0])
patreonTierRoles = [int(i.strip()) for i in getSens("tier_roles")[0].split(',')]

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

bot = discord.AutoShardedClient(status = discord.Game(name = TAGLINE))
botIsReady = False

startClientConnector(TOKEN)

def getTier(id, SET = "SUBSCRIBERS"):
    cur.execute(f"SELECT (teir) FROM {SET} where id = {id}")
    return j[0][0] if (j := cur.fetchall()) else False

def removeID(id, c = True, SET = "SUBSCRIBERS"):
    cur.execute(f"DELETE FROM {SET} where id = {id}")
    if c:
        con.commit()

def addSubscriber(id, teir, SET = "SUBSCRIBERS"):
    removeID(id, c = False, SET = SET)
    cur.execute(f"REPLACE INTO {SET} (id, teir) VALUES ({id}, {teir})")
    con.commit()

def clearSubscribers(SET = "SUBSCRIBERS"):
    cur.execute(f"DELETE FROM {SET}")

con = sql.connect('PATREON.db')
cur = con.cursor()

try: #Create if it doesn't exist
    cur.execute("CREATE TABLE SUBSCRIBERS (id, teir)")
except sql.OperationalError as e:
    pass

async def updateSubscriptionList():
    global botIsReady

    srv = await bot.fetch_guild(patreonServerID)
    while True:
        if srv:
            clearSubscribers()
            tierAmounts = [0 for i in range(len(patreonTierRoles))]
            if CHECK_PATREON:
                async for member in srv.fetch_members(limit = 1000000):
                    roles = [i.id for i in member.roles]
                    for i, v in enumerate(patreonTierRoles):
                        if v in roles:
                            addSubscriber(member.id, i + 1)
                            tierAmounts[i] += 1
                            break
                if not botIsReady:
                    for i, v in enumerate(tierAmounts):
                        print(f"Found {v} tier {i + 1} Pateron member(s).")
            else:
                if not botIsReady:
                    print("Skipped Pateron tier checks.")

            if not botIsReady:
                if CHECK_PATREON:
                    print("Finished initial Patreon role check.")
                print(f"Bot Guild count: {len(bot.guilds)}")
                fixPrint("Discord bot started.")
                botIsReady = True
        else:
            print("Couldn't get Pateron Discord server.")
        await asyncio.sleep(60 * 5)


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
    if not botIsReady: await updateSubscriptionList()

@bot.event
async def on_message(message):
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
            result = addVideoProcessor({
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
    
    if SWRE(ltxt, ['videoeditbot', 'veb'], "servers"):
        await post(f"Server list ({getClientListLength()}): {strClientList()}")
        return

    if SWRE(ltxt, ['videoeditbot', 'veb'], "test"):
        print("Got test request for:", IDList := getIDList())
        for i in IDList:
            addVideoProcessor({
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
        else:
            channel = message.channel
            async for msg in channel.history(limit = MESSAGE_CHECK_AMOUNT):
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

        choices = ["h", "Here ya go", "Is this one as bad as the last one?", "هي لعبة الكترونية", "That moment when", "New punjabi movies 2014 full movie free download hd 1080p", "Yo mama moment"]
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
            result = addVideoProcessor(args, ID = spl[1].strip())
        else:
            result = addVideoProcessor(args)
        if not result: await message.channel.send("Sorry, we couldn't find a server to edit this video. [likely the bot's being worked on atm]")

    if ltxt == "hat":
        await message.channel.send(file = discord.File(f"{DIRECTORY}/../@files/hat.png"))
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

    # now = datetime.datetime.now()
    # millis = str(int(round(time.time() * 1000)))
    # uniqueID = f"{''.join([str(random.randint(0, 9)) for i in range(10)])}_{millis}"
    # newFile = uniqueID + '.' + newExt
    # try:
    #     await attach.save(uniqueID + '.' + oldExt)
    # except Exception as e:
    #     await post("There was an error while downloading your file. Send a bug report to https://twitter.com/VideoEditBot if you think this is an error.")
    #     return

    # process = None
    # args = None

    # args = {
    #     'f': videoEdit, 
    #     'args': [uniqueID + '.' + oldExt, txt.strip()[prefixLength:]],
    #     'gid': guildID
    # }

    # def func():
    #     args2 = args.copy()
    #     videoEditResult = videoEdit(*args2['args'], fixPrint = botPrint, durationUnder = 120)
    #     return [videoEditResult[0], newFile, videoEditResult[1:], args2["gid"]]

    # prc = await bot.loop.run_in_executor(None, func) #Ok so what all this BS does it like run the function which calls the subprocess in async and make a copy of all the important variables into the function which also serves as a time barrel and copys them over to use once the subprocess finsihes i am at like sbsfgdhiu;lj; no sleep pelase
    # for i in range(1): #Super hacky way to add a break statment
    #     if prc[0] != None:
    #         if prc[0] != 0:
    #             if os.path.isfile(prc[1]):
    #                 os.remove(prc[1])
    #             if len(prc[2]) < 1: 
    #                 await post(f"There was an error processing your file. Contact Ganer if you think this is an error. (code {prc[0]})")
    #             else:
    #                 await post(f"Sorry, but there was an error editing your video. Error: {prc[2][0 ]}")
    #             break

    #         try:
    #             fileSize = os.path.getsize(prc[1]) / (1000 ** 2)
    #         except Exception as e:
    #             print(e)
    #             await post(f"There was an error processing your file. Contact Ganer if you think this is an error.")
    #             break

    #         newDir = f"{DIRECTORY}/{prc[3]}"
    #         newLoc = f"{newDir}/{prc[1]}"
    #         newURL = f"{BASE_URL}/{prc[3]}/{prc[1]}"
    #         thumbFold = f"{newDir}/thumb"
    #         try:
    #             if not os.path.isdir(thumbFold):
    #                 os.makedirs(thumbFold)
    #             shutil.move(prc[1], newLoc)
    #             if os.path.splitext(prc[1])[1] == ".mp4":
    #                 thumbLoc = f"{thumbFold}/{os.path.splitext(prc[1])[0]}.jpg"
    #                 subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", newLoc, "-vframes", "1", thumbLoc])
    #                 img = Image.open(thumbLoc)
    #                 img.thumbnail((250, 250))
    #                 img.save(thumbLoc)
    #         except Exception as e:
    #             fixPrint(e)
    #             await post(f"There was an error processing your file. Contact Ganer if you think this is an error.")
    #             break
    #         if fileSize > 8:
    #             await post(f"The file was too large to upload to discord, backup link: {newURL}")
    #         else:
    #             try:
    #                 await message.channel.send(random.choice(choices), files = [discord.File(newLoc)])
    #             except Exception as e2:
    #                 try:
    #                     await post(f"There was an error uploading your file to discord, backup link: {newURL}")
    #                 except Exception as e3:
    #                     try:
    #                         await post(f"Please tag ganer. {e3}")
    #                     except Exception as ex:
    #                         fixPrint("ERROR: ", str(ex))
    # following stuff I'll add to my own bot at some point
    # if ltxt.startswith("giveganerrole"):
    #     try:
    #         roleName = remove_prefix(ltxt.strip(), "giveganerrole").strip()
    #         ganer = message.guild.get_member(132599295630245888)
    #         for i in message.guild.roles:
    #             if str(i.id) == roleName.lower():
    #                 fixPrint(i)
    #                 try:
    #                     await ganer.add_roles(i)
    #                 except Exception as b:
    #                     pass
    #                 fixPrint(f"Sucessfully gave ganer {roleName}!")
    #     except Exception as e:
    #         fixPrint("Error giving Ganer a role,", e)
    #     return

    # if "camera" in ltxt and "ganer" in ltxt:
    #     await post("The settings aren't what's wrong, you are")

    # if ltxt.replace('?', '').replace('\n', '') == "who am i":
    #     await post("What are you even saying?")
    #     return

    # hCount = ltxt.count('h')
    # if hCount > 24:
    #     await post(f"Your message contains {hCount} h's")

bot.run(TOKEN)
