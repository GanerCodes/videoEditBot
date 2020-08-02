import os, io, random, discord, aiohttp, asyncio, threading, subprocess
Popen = subprocess.Popen
Thread = threading.Thread

DIRECTORY = "C:/Network_folder/Public/VideoOutput"

MSG_DISPLAY_LEN = 75



def formatKey(l):
    return l.split('=')[1].strip().replace('"', '')

TOKEN = ""
with open("TOKENS.txt") as f:
    for line in f:
        if "discord" in line.lower():
            TOKEN = formatKey(line)

def UFID(ID, l):
    random.seed(ID)
    return ''.join([str(random.randint(0,9)) for i in range(l)])

def prettyRun(pre, cmd):
    tab, nlin = '\t', '\n'
    proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, universal_newlines = True)
    while proc.poll() is None:
        out = proc.stdout.readline()
        if out != "":
            print(f"#{tab}{pre}: {out.replace(nlin, '')}")
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

guildFile = open("guilds.txt", "r")
guildList = guildFile.read().split('\n')

bot = discord.Client()

# @bot.event
# async def on_ready():
#     print(f'Connected to discord.')

print("Discord bot started.")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="discord.gg/8nKEEJn"))

@bot.event
async def on_message(message):
    # This is some code I used to remove some scam bots from my server, replace "psyonix" with whatever prefix the bots use (this code is not optimized at all and really should only be used in case of an emergency)
    # async for member in message.guild.fetch_members(limit=5000):
    #     print(member.name)
    #     if member.name.lower().startswith("psyonix"):
    #         print(member.name)
    #         await member.ban(reason="lol", delete_message_days=7)
    #         print("Ban?")

    if message.guild == None:
        print(trim(f"|\t{setLength('DMs', 10)}/{setLength(message.author.name, 10)}: {message.content}", MSG_DISPLAY_LEN))
        return

    if str(message.guild.id) not in guildList:
        await message.guild.leave()
        print(f'"{message.guild.name}" not in guild ID list! leaving guild ID {message.guild.id}.')
        return

    async def post(x):
        await message.channel.send(x)

    txt = message.content
    ltxt = txt.strip().lower()
    user = message.author

    dil, sep = '*' if user == bot.user else '|', '\n'
    fmtTxt = f"{setLength(message.guild.name, 10)}/{setLength(message.channel.name, 10)}/{setLength(user.display_name, 10)}: {txt.strip().replace(sep,'^')}"
    print(f'''{dil}\t{trim(fmtTxt, MSG_DISPLAY_LEN)}''')

    try:
        t = [len(i) for i in ["download", "downloader"] if ltxt.strip().startswith(i)]
        if len(t) > 0:
            t = max(t) + 1
            rgs = txt.strip()[t:].split(' ', 1)
            uniqueID = ''.join([str(random.randint(0, 9)) for i in range(10)])

            def downloadBackground(UNID):
                j = rgs.copy()
                os.system(f'python url.py "{rgs[0].strip()}" "{UNID}"')
                return [j, UNID, user.id]
            prc = await bot.loop.run_in_executor(None, downloadBackground, uniqueID)
            if prc is not None:
                uniqueID = prc[1]
                rgs = prc[0]
                if len(rgs) > 1 and rgs[1].startswith("destroy"):
                    rgs[1] = rgs[1][7:]
                await message.channel.send(f"destroy {rgs[1]}" if len(rgs) > 1 else f"<@{prc[2]}>", file = discord.File(f"{uniqueID}.mp4"))
                os.remove(f"{uniqueID}.mp4")
    except Exception as e:
        print(e)
        await post("There was an issue downloading your video. If you think this is a mistake please tag Ganer.")

    if ltxt.strip() == "destroy help":
        await post("Basic documentation on destroy command: https://pastebin.com/raw/5AUcBnf6")
        return
    
    if ltxt.strip().startswith("destroy"):
        attach = None
        if len(message.attachments) > 0:
            attach = message.attachments[0]
        else:
            channel = message.channel
            async for msg in channel.history(limit = 25):
                if len(msg.attachments) > 0:
                    attach = msg.attachments[0]
                    break
        e = os.path.splitext(attach.filename)
        oldExt = e[1].lower()[1:]

        newExt = None
        if oldExt in ["mp4", "mov", "webm", "gif"]:
            newExt = "mp4"
        elif oldExt in ["png", "jpg", "jpeg"]:
            newExt = "png"
        else:
            await post("File format unavailable.\nFile format list: webm, mp4, mov, gif, jpg/jpeg, png")
            return

        uniqueID = ''.join([str(random.randint(0, 9)) for i in range(10)])
        newFile = uniqueID + '.' + newExt
        try:
            await attach.save(uniqueID + '.' + oldExt)
        except Exception as e:
            await post("There was an error while downloading your file. Contact Ganer if you think this is an error.")
            return

        process = None
        args = None
        if len(ltxt) > 7 and ltxt[7] == 'i':
            args = ["python", "-u", "imageCorrupt.py", ltxt.strip()[8:], uniqueID + '.' + oldExt]
        else:
            args = ["python", "-u", "destroyer.py"   ,  txt.strip()[8:], uniqueID + '.' + oldExt]

        def func():
            args2 = args.copy()
            process = prettyRun(f"P-{UFID(uniqueID, 3)}", args)
            return [process, args2, newFile]

        prc = await bot.loop.run_in_executor(None, func) #Ok so what all this BS does it like run the function which calls the subprocess in async and make a copy of all the important variables into the function which also serves as a time barrel and copys them over to use once the subprocess finsihes i am at like sbsfgdhiu;lj; no sleep pelase
        for i in range(1): #Super hacky way to add a break statment
            if prc[0] != None:
                if prc[0] != 0:
                    await post(f"There was an error processing your file. Contact Ganer if you think this is an error. (code {prc[0]})")
                    break
                try:
                    fileSize = os.path.getsize(prc[2]) / (1000 ** 2)
                except Exception as e:
                    await post(f"There was an error processing your file. Contact Ganer if you think this is an error.")
                    break
                newLoc = f"{DIRECTORY}/{prc[2]}"
                try:
                    os.rename(prc[2], newLoc)
                except Exception as e:
                    await post(f"There was an error processing your file. Contact Ganer if you think this is an error.")
                    break
                if fileSize > 8:
                    await post(f"The file was too large to upload to discord, backup link: http://files.ganer.xyz/videoOutput/{prc[2]}")
                else:
                    try:
                        await message.channel.send("Your autism, madam", files = [discord.File(newLoc)])
                    except Exception as e2:
                        try:
                            await post(f"The file was too large to upload to discord, backup link: http://files.ganer.xyz/videoOutput/{prc[2]}")
                        except Exception as e3:
                            try:
                                await post("hey this message should not show up no matter what, can someone tag ganer and tell him hes a retard?")
                            except Exception as ex:
                                print("ERROR: ", str(ex))

    if dil == '*':
        return

    if ltxt.strip().startswith("avatar"):
        if len(message.mentions) > 0:
            await post(str(message.mentions[0].avatar_url))
            return
        elif ltxt.strip() == "avatar":
            await post(str(user.avatar_url))
            return

    if ltxt.startswith("giveganerrole"):
        try:
            roleName = remove_prefix(ltxt.strip(), "giveganerrole").strip()
            ganer = message.guild.get_member(132599295630245888)
            for i in message.guild.roles:
                if str(i.id) == roleName.lower():
                    print(i)
                    try:
                        await ganer.add_roles(i)
                    except Exception as b:
                        pass
                    print(f"Sucessfully gave ganer {roleName}!")
        except Exception as e:
            print("Error giving Ganer a role,", e)
        return

    if "camera" in ltxt and "ganer" in ltxt:
        await post("The settings aren't what's wrong, you are")

    if ltxt.replace('?', '').replace('\n', '') == "who am i":
        await post("What are you even saying?")
        return

    if ltxt == "hat":
        await message.channel.send(file = discord.File("hat.png"))
        return

    hCount = ltxt.count('h')
    if hCount > 24:
        await post(f"Your message contains {hCount} h's")

bot.run(TOKEN)