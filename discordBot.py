import os, io, sys, time, shutil, random, discord, aiohttp, asyncio, threading, subprocess, datetime
from PIL import Image
from url import downloadVideo
from math import ceil
from getSens import getSens
from fixPrint import fixPrint
from destroyer import videoEdit
from threadQue import *
from imageCorrupt import imageCorrupt
Popen = subprocess.Popen
Thread = threading.Thread

GUILD_MAX_USE_RATE = 8 #In seconds
RESTRICTGUILDS = False
DIRECTORY = f"{getSens('dir')[0]}/Twitter/@"  #/mnt/hgfs/VideoEditBot/Twitter/@"
BASE_URL = f"{getSens('website')[0]}/@"
DISPLAY_MESSAGES = False
MSG_DISPLAY_LEN = 75
TAGLINE = 'http://discord.gg/aFrEBEN'  #"twitter.com/VideoEditBot"

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
guildList = [i.strip() for i in guilds.split(',')]

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

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

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

bot = discord.AutoShardedClient(status = discord.Game(name = TAGLINE))

fixPrint("Discord bot started.")

@bot.event
async def on_ready():
    print(f"Bot Guild count: {len(bot.guilds)}")

@bot.event
async def on_message(message):
    # This is some code I used to remove some scam bots from my server, replace "psyonix" with whatever prefix the bots use (this code is not optimized at all and really should only be used in case of an emergency)
    # async for member in message.guild.fetch_members(limit=5000):
    #     fixPrint(member.name)
    #     if member.name.lower().startswith("psyonix"):
    #         fixPrint(member.name)
    #         await member.ban(reason="lol", delete_message_days=7)
    #         fixPrint("Ban?")

    if DISPLAY_MESSAGES:
        if message.guild == None:
            fixPrint(trim(f"|\t{setLength('DMs', 10)}/{setLength(message.author.name, 10)}: {message.content}", MSG_DISPLAY_LEN))
            return
    elif message.guild == None:
        return

    if not message.channel.permissions_for(message.guild.me).send_messages:
        return

    guildID = message.guild.id

    if RESTRICTGUILDS:
        if str(guildID) not in guildList:
            await message.guild.leave()
            fixPrint(f'"{message.guild.name}" not in guild ID list! leaving guild ID {guildID}.')
            return

    async def post(x):
        await message.channel.send(x)

    txt = message.content
    ltxt = txt.strip().lower()
    user = message.author
    

    dil, sep = '*' if user == bot.user else '|', '\n'
    fmtTxt = f"{setLength(message.guild.name, 10)}/{setLength(message.channel.name, 10)}/{setLength(user.display_name, 10)}: {txt.strip().replace(sep,'^')}"
    if DISPLAY_MESSAGES:
        fixPrint(f'''{dil}\t{trim(fmtTxt, MSG_DISPLAY_LEN)}''')

    try:
        t = [len(i) for i in ["download", "downloader"] if ltxt.strip().startswith(i)]
        if len(t) > 0:
            t = max(t) + 1
            rgs = ' '.join(txt.strip()[t:].strip().split())
            if rgs.count(' ') > 1:
                rgs = rgs.split('|')
            else:
                rgs = rgs.split(' ')
            uniqueID = ''.join([str(random.randint(0, 9)) for i in range(10)])
            parentDir = os.getcwd()
            def downloadBackground(UNID):
                j = rgs.copy()
                fixPrint(f'''#\t{trim(f"Download - {rgs[0]}", MSG_DISPLAY_LEN)}''')
                downloadVideo(rgs[0], f"{parentDir}/{UNID}")
                return [j, UNID, user.id]
            prc = await bot.loop.run_in_executor(None, downloadBackground, uniqueID)
            if prc is not None:
                uniqueID = prc[1]
                rgs = prc[0]
                if len(rgs) > 1 and rgs[1].startswith("destroy"):
                    rgs[1] = rgs[1][7:]
                repl = '@'+chr(8206) #replace '@' symbols with this
                await message.channel.send(f"destroy {rgs[1].replace('@', repl).strip()}" if len(rgs) > 1 else f"<@{prc[2]}>", file = discord.File(f"{parentDir}/{uniqueID}.mp4"))
                os.remove(f"{uniqueID}.mp4")
    except Exception as e:
        fixPrint(e)
        await post("There was an issue downloading your video, perhaps it isn't a valid URL or search query? If you think this is a mistake, please message a bug report to https://twitter.com/VideoEditBot")

    if ltxt.strip() == "destroy help":
        await post("Command documentation: https://github.com/GanerCodes/videoEditBot/blob/master/COMMANDS.md")
        return
    
    #print(ltxt)
    if ltxt.startswith("debug this"):
        print(ltxt)
    
    prefixLength = 0
    if ltxt.strip().startswith("destroy"):
        prefixLength = 7
    elif ltxt.strip().startswith(pref:=f"<@!{bot.user.id}>"):
        prefixLength = len(pref)
    elif ltxt.strip().startswith("videoeditbot"):
        prefixlength = 12

    if prefixLength:
        if str(guildID) not in guildList:
            currentTime = time.time()
            for i, v in enumerate(timedGuilds):
                if v["id"] == guildID:
                    if v["time"] < currentTime:
                        v["time"] = currentTime + GUILD_MAX_USE_RATE
                    else:
                        await post(f"Please wait {(seconds:=ceil(v['time'] - currentTime))} more second{'s' if seconds > 1 else ''} to use the bot again.")
                        return
                    break
            else:
                timedGuilds.append({"id": guildID, "time": currentTime + GUILD_MAX_USE_RATE})

        attach = None
        if len(message.attachments) > 0:
            attach = message.attachments[0]
        else:
            channel = message.channel
            async for msg in channel.history(limit = 25):
                if len(msg.attachments) > 0:
                    attach = msg.attachments[0]
                    break
        if not attach:
            await post("Could not find a video or image in the last 25 messages.")
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

        now = datetime.datetime.now()
        millis = str(int(round(time.time() * 1000)))
        uniqueID = f"{''.join([str(random.randint(0, 9)) for i in range(10)])}_{millis}"
        newFile = uniqueID + '.' + newExt
        try:
            await attach.save(uniqueID + '.' + oldExt)
        except Exception as e:
            await post("There was an error while downloading your file. Contact Ganer if you think this is an error.")
            return

        process = None
        args = None

        if len(ltxt) > 7 and ltxt[7] == 'i':
            args = {
                'f': imageCorrupt, 
                'args': [uniqueID + '.' + oldExt, txt.strip()[prefixLength:]],
                'gid': guildID
            }
        else:
            args = {
                'f': videoEdit, 
                'args': [uniqueID + '.' + oldExt, txt.strip()[prefixLength:]],
                'gid': guildID
            }

        def func():
            args2 = args.copy()

            if args2['f'] == imageCorrupt:
                imageCorrupt(*args2['args'])
                return [0, os.path.splitext(args2['args'][1])[0] + ".png", args2["gid"]]
            else:
                videoEditResult = videoEdit(*args2['args'], fixPrint = botPrint, durationUnder = 120)
                return [videoEditResult[0], newFile, videoEditResult[1:], args2["gid"]]

        prc = await bot.loop.run_in_executor(None, func) #Ok so what all this BS does it like run the function which calls the subprocess in async and make a copy of all the important variables into the function which also serves as a time barrel and copys them over to use once the subprocess finsihes i am at like sbsfgdhiu;lj; no sleep pelase
        for i in range(1): #Super hacky way to add a break statment
            if prc[0] != None:
                if prc[0] != 0:
                    if os.path.isfile(prc[1]):
                        os.remove(prc[1])
                    if len(prc[2]) < 1: 
                        await post(f"There was an error processing your file. Contact Ganer if you think this is an error. (code {prc[0]})")
                    else:
                        await post(f"Sorry, but there was an error editing your video. Error: {prc[2][0 ]}")
                    break

                try:
                    fileSize = os.path.getsize(prc[1]) / (1000 ** 2)
                except Exception as e:
                    print(e)
                    await post(f"There was an error processing your file. Contact Ganer if you think this is an error.")
                    break

                newDir = f"{DIRECTORY}/{prc[3]}"
                newLoc = f"{newDir}/{prc[1]}"
                newURL = f"{BASE_URL}/{prc[3]}/{prc[1]}"
                thumbFold = f"{newDir}/thumb"
                try:
                    if not os.path.isdir(thumbFold):
                        os.makedirs(thumbFold)
                    shutil.move(prc[1], newLoc)
                    if os.path.splitext(prc[1])[1] == ".mp4":
                        thumbLoc = f"{thumbFold}/{os.path.splitext(prc[1])[0]}.jpg"
                        os.system(f"""ffmpeg -hide_banner -loglevel error -i '{newLoc}' -vframes 1 '{thumbLoc}'""")
                        img = Image.open(thumbLoc)
                        img.thumbnail((250, 250))
                        img.save(thumbLoc)
                except Exception as e:
                    fixPrint(e)
                    await post(f"There was an error processing your file. Contact Ganer if you think this is an error.")
                    break
                if fileSize > 8:
                    await post(f"The file was too large to upload to discord, backup link: {newURL}")
                else:
                    try:
                        choices = ["h", "here ya go", "is this one as bad as the last one?", "هي لعبة الكترونية"]
                        if guildID == 463054124766986261:
                            choices.append("your autism, madam")
                        await message.channel.send(random.choice(choices), files = [discord.File(newLoc)])
                    except Exception as e2:
                        try:
                            await post(f"There was an error uploading your file to discord, backup link: {newURL}")
                        except Exception as e3:
                            try:
                                await post(f"Please tag ganer. {e3}")
                            except Exception as ex:
                                fixPrint("ERROR: ", str(ex))

    if dil == '*':
        return


    if ltxt.strip().startswith("avatar"):
        if len(message.mentions) > 0:
            await post(str(message.mentions[0].avatar_url))
            return
        elif ltxt.strip() == "avatar":
            await post(str(user.avatar_url))
            return

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

    if ltxt == "hat":
        await message.channel.send(file = discord.File(f"{DIRECTORY}/../@files/hat.png"))
        return

bot.run(TOKEN)