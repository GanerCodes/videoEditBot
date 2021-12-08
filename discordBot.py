import os, sys, time, json, random, discord, requests, asyncio, logging
from editor.download import download
from collections import namedtuple
from threading import Thread
from functools import reduce
from operator import add
from editor import editor

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_handler = logging.StreamHandler(sys.stdout)
logger_handler.setLevel(logging.DEBUG)
logger.addHandler(logger_handler)
info = lambda *args: logger.info(' | '.join(map(str, args)))

config = json.load(open("config.json", 'r'))

message_search_count = int(config["message_search_count"])
command_chain_limit  = int(config["command_chain_limit"])
working_directory    = os.path.realpath(config["working_directory"])
discord_tagline      = config["discordTagline"]
discord_token        = config["discordToken"]
meta_prefixes        = config["meta_prefixes"]
cookie_file          = config["cookie_file"] if "cookie_file" in config else None

valid_extensions = ["mp4", "webm", "avi", "mkv", "mov", "png", "gif", "jpg", "jpeg"]

taskList, messageQue = [], []
botReady = False

if not os.path.isdir(working_directory): os.makedirs(working_directory)
intents = discord.Intents.default()
intents.messages = True # intents.members = True
discord_status = discord.Game(name = discord_tagline)
bot = discord.AutoShardedClient(status = discord_status, intents = intents)

dynamic_task = namedtuple("dynamic_task", "context name func args kwargs", defaults = 5 * ' ')
qued_msg     = namedtuple("qued_msg"    , "context name result"          , defaults = 3 * ' ')
result       = namedtuple("result"      , "success filename message"     , defaults = 3 * ' ')

class target_group:
    def __init__(self, attachments, reply, channel):
        self.attachments = attachments
        self.reply       = reply
        self.channel     = channel
    def compile(self):
        return self.attachments + self.reply + self.channel

def same_tuple_type(a, b):
    return type(a).__name__ == b.__name__

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
        
        if same_tuple_type(res.result, dynamic_task):
            run_seperate_add_que_redirect(res.result)
            continue
        
        if same_tuple_type(res.result, result):
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

async def get_targets(msg, attachments = True, reply = True, channel = True, message_search_count = 8, stop_on_first = True):
    msg_attachments, msg_reply, msg_channel = [], [], []
    
    async def do_setters():
        nonlocal msg_attachments, msg_reply, msg_channel
        if attachments: msg_attachments = msg.attachments
        if stop_on_first and msg_attachments: return
        
        if reply and msg.reference: msg_reply = (await msg.channel.fetch_message(msg.reference.message_id)).attachments
        if stop_on_first and msg_reply: return
        
        if channel and message_search_count > 0: msg_channel = reduce(add, [i.attachments async for i in msg.channel.history(limit = message_search_count)])
    await do_setters()
    
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
    targets = (await get_targets(msg, message_search_count = message_search_count)).compile()
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
    run_seperate_add_que(msg, "download", download, f"{generate_uuid_from_msg(msg.id)}.mp4", arg, duration = 60, cookies = cookie_file)

async def parse_command(message):
    msg = message.content
    if len(msg) == 0: return
    
    has_meta_prefix = message.reference and (await message.channel.fetch_message(message.reference.message_id)).author.id == bot.user.id
    append_space = ' ' if ' ' in msg else ''
    for pre in meta_prefixes:
        if msg.startswith(pre + append_space):
            has_meta_prefix = True
            msg = msg.removeprefix(pre).lstrip()
            break
    
    commands = msg.split(">>")[:command_chain_limit]
    
    command = commands[0]
    chained = '>>'.join(command[1:])
    spl = command.strip().split(' ', 1)
    cmd  = spl[0].strip().lower()
    args = spl[1].strip() if len(spl) > 1 else ""
    if cmd in ["destroy", ""]:
        await prepare_VideoEdit(message, args)
    elif cmd == "concat":
        pass
        # await prepare_VideoEdit(message, args)
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
    info("Bot ready!")

@bot.event
async def on_message(msg):
    await parse_command(msg)

bot.run(discord_token)