import os, json, random, discord, asyncio
from collections import namedtuple
from editor import editor
from threading import Thread

config = json.load(open("config.json", 'r'))

intents = discord.Intents.default()
intents.messages = True
# intents.members = True
discord_status = discord.Game(name = config["discordTagline"])
bot = discord.AutoShardedClient(status = discord_status, intents = intents)
botReady = False

qued_msg = namedtuple("qued_msg", ["context", "name", "result"])

taskList, messageQue = [], []
def run_seperate_add_que(context, name, func, *args, **kwargs):
    Thread(
        target = lambda: messageQue.append(
            qued_msg(
                context, name, func(*args, **kwargs)
            )
        )
    ).start()


async def processQue():
    while True:
        while len(messageQue):
            res = messageQue.pop(0)
            if res.name == "editor":
                if res.result.success:
                    with open(res.result.filename, 'rb') as f:
                        await res.context.reply(
                            random.choice(config["response_messages"]),
                            file = discord.File(f,
                                filename = f"{res.context.id}{os.path.splitext(res.result.filename)[1]}"
                            )
                        )
                else:
                    await res.context.reply(res.result.message)
                    
        await asyncio.sleep(1)
        

# download things >> destroy args
async def parse_command(msg):
    commands = msg.content.split(">>")[:2]
    for command in commands:
        spl = command.strip().split(' ', 1)
        cmd = spl[0].strip().lower()
        arg = spl[1].strip() if len(spl) == 2 else ""
        if cmd == "destroy":
            run_seperate_add_que(msg, "editor", editor, "hi.mp4", arg, workingDir = "./active", keep_original_file = True)
        elif cmd == "concat":
            pass
        elif cmd == "download":
            pass
        await msg.channel.send(f"Got command: {cmd} | {arg}")

@bot.event
async def on_ready():
    global botReady
    if botReady: pass
    
    botReady = True
    await bot.change_presence(activity = discord_status)
    asyncio.create_task(processQue())
    print("Bot ready!")

@bot.event
async def on_message(msg):
    if msg.content.lower().strip().split(' ', 1)[0] in ("destroy", "copncat", "download"): #add alisases
        await parse_command(msg)

bot.run(config["discordToken"])