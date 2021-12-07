import os, time, json, random, discord, requests, asyncio
from collections import namedtuple
from threading import Thread
from editor import download, editor

config = json.load(open("config.json", 'r'))

message_search_count = int(config["message_search_count"])
working_directory   = os.path.realpath(config["working_directory"])
discord_tagline     = config["discordTagline"]
discord_token       = config["discordToken"]
meta_prefixes       = config["meta_prefixes"]
cookie_file         = config["cookie_file"] if "cookie_file" in config else None

valid_extensions = ["mp4", "webm", "avi", "mkv", "mov", "png", "gif", "jpg", "jpeg"]


if not os.path.isdir(working_directory): os.makedirs(working_directory)
intents = discord.Intents.default()
intents.messages = True
# intents.members = True
discord_status = discord.Game(name = discord_tagline)
bot = discord.AutoShardedClient(status = discord_status, intents = intents)
botReady = False

result = namedtuple("result", ["success", "filename", "message", "asdf"])
dynamic_task = namedtuple("dynamic_task", ["context", "name", "func", "args", "kwargs"])
qued_msg = namedtuple("qued_msg", ["context", "name", "result"])

class target_group:
    def __init__(self, attachments, reply, channel):
        self.attachments = attachments
        self.reply       = reply
        self.channel     = channel
    def compile(self):
        return self.attachments + self.reply + self.channel

taskList, messageQue = [], []
def run_seperate_add_que(context, name, func, *args, **kwargs):
    Thread(
        target = lambda: messageQue.append(
            qued_msg(
                context, name, func(*args, **kwargs)
            )
        )
    ).start()

def run_seperate_add_que_redirect(task):
    run_seperate_add_que(task.context, task.name, task.func, *task.args, **task.kwargs)

async def processQue():
    while True:
        if not len(messageQue):
            await asyncio.sleep(1)
            continue
        
        res = messageQue.pop(0)
        
        if type(res.result) == dynamic_task:
            run_seperate_add_que_redirect(res.result)
            continue
        
        if type(res.result) == result:
            if res.result.success:
                with open(res.result.filename, 'rb') as edited_file:
                    await res.context.reply(
                        random.choice(config["response_messages"]),
                        file = discord.File(
                            edited_file,
                            filename = f"{res.context.id}{os.path.splitext(res.result.filename)[1]}"
                        )
                    )
            else:
                await res.context.reply(res.result.message)
                


async def get_targets(msg, attachments = True, reply = True, channel = True, stop_on_first = True):
    msg_attachments = msg.attachments if attachments else []
    if stop_on_first and msg_attachments: return target_group(msg_attachments, [], [])
        
    msg_reply = (await msg.channel.fetch_message(msg.reference.message_id)).attachments if reply and msg.reference else []
    if stop_on_first and msg_reply: return target_group([], msg_reply, [])
    
    if message_search_count > 0 and channel:
        msg_channel = []
        async for i in msg.channel.history(limit = message_search_count):
            msg_channel += i.attachments
    else:
        msg_channel = []
    
    return target_group(msg_attachments, msg_reply, msg_channel)

def veb_discord_download(msg, target, filename, veb_args):
    r = requests.get(target.url)
    with open(filename, 'wb') as f:
        f.write(r.content)
    
    run_seperate_add_que_redirect(dynamic_task(
        msg, "editor", editor, [filename, veb_args], {
            "workingDir": working_directory,
            "keepExtraFiles": True
        }
    ))

def generate_uuid_from_msg(msg_id):
    return f"{working_directory}/{msg_id}_{(time.time_ns() // 100) % 1000000}"

async def prepare_VideoEdit(msg, arg):
    targets = (await get_targets(msg)).compile()
    if not targets:
        await msg.channel.send("Unable to find a message to edit, maybe upload a video and try again?")
        return
    
    file_ext = os.path.splitext(targets[0].filename)[1][1:]
    if file_ext not in valid_extensions:
        await msg.channel.send(f"File type not valid, valid file types are: `{'`, `'.join(valid_extensions)}`")
        return
    
    filename = f"{generate_uuid_from_msg(msg.id)}{file_ext}"
    run_seperate_add_que(msg, "veb_discord_download", veb_discord_download, msg, targets[0], filename, arg)

async def prepare_download(msg, arg):
    run_seperate_add_que(msg, "download", download, f"{generate_uuid_from_msg(msg.id)}.mp4", arg, cookies = cookie_file)

async def parse_command(message):
    msg = message.content
    if len(msg) == 0: return
    
    has_meta_prefix = message.reference and (await message.channel.fetch_message(message.reference.message_id)).author.id == bot.user.id
    for pre in meta_prefixes:
        if msg.startswith(pre):
            has_meta_prefix = True
            msg = msg.removeprefix(pre).lstrip()
            break
    
    commands = msg.split(">>")[:2]
    for command in commands:
        spl = command.strip().split(' ', 1)
        cmd  = spl[0].strip().lower()
        args = spl[1].strip() if len(spl) > 1 else ""
        if cmd in ["destroy", ""]:
            await prepare_VideoEdit(message, args)
        elif cmd == "concat":
            await prepare_VideoEdit(message, args)
        elif cmd == "download":
            await prepare_download(message, args)
        elif has_meta_prefix: # Tags veb, replies to veb, etc
            await prepare_VideoEdit(message, f"{cmd} {args}")

@bot.event
async def on_ready():
    global meta_prefixes, botReady
    if botReady: pass
    
    meta_prefixes += [
         f"<@{bot.user.id}>",
        f"<@!{bot.user.id}>",
        f"<@&{bot.user.id}>",
        f"<@#{bot.user.id}>",
    ]
    await bot.change_presence(activity = discord_status)
    asyncio.create_task(processQue())
    botReady = True
    print("Bot ready!")

@bot.event
async def on_message(msg):
    await parse_command(msg)

bot.run(discord_token)