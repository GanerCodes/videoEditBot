import os, sys, time, json, random, discord, requests, asyncio, logging
from combiner import combiner
from editor.download import download
from collections import namedtuple
from func_helper import  *
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

message_search_count = config["message_search_count"]
command_chain_limit  = config["command_chain_limit"]
working_directory    = os.path.realpath(config["working_directory"])
response_messages    = config["response_messages"]
max_concat_count     = config["max_concat_count"]
discord_tagline      = config["discord_tagline"]
discord_token        = config["discord_token"]
meta_prefixes        = config["meta_prefixes"]
cookie_file          = config["cookie_file"] if "cookie_file" in config else None

valid_video_extensions = ["mp4", "webm", "avi", "mkv", "mov"]
valid_image_extensions = ["png", "gif", "jpg", "jpeg"]
valid_extensions = valid_video_extensions + valid_image_extensions

async_runner = Async_handler()
taskList, messageQue = [], []
botReady = False

if not os.path.isdir(working_directory): os.makedirs(working_directory)
intents = discord.Intents.default()
intents.messages = True # intents.members = True
discord_status = discord.Game(name = discord_tagline)
bot = discord.AutoShardedClient(status = discord_status, intents = intents)

qued_msg = namedtuple("qued_msg", "context message filepath filename reply edit", defaults = 6 * [None])
result = namedtuple("result", "success filename message", defaults = 3 * [None])

class target_group:
    def __init__(self, attachments, reply, channel):
        self.attachments = attachments
        self.reply       = reply
        self.channel     = channel
    def compile(self):
        return self.attachments + self.reply + self.channel

def generate_uuid_from_msg(msg_id):
    return f"{msg_id}_{(time.time_ns() // 100) % 1000000}"

def generate_uuid_folder_from_msg(msg_id):
    return f"{working_directory}/{generate_uuid_from_msg(msg_id)}"

def clean_message(msg):
    return msg.replace('@', '@'+chr(8206))

async def processQue():
    while True:
        if not len(messageQue):
            await asyncio.sleep(1)
            continue
            
        res = messageQue.pop(0)
        
        action = res.context.reply if res.reply else (res.context.edit if res.edit else res.context.channel.send)
        if res.filename:
            with open(res.filename, 'rb') as file:
                args = [res.message] if res.message else []
                file_kwargs = {"filename": res.filename} if res.filename else {}
                await action(*args, file = discord.File(file, **file_kwargs))
        else:
            await action(res.message)

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

def download_discord_attachment(target, filename, keep_ext = False):
    if keep_ext:
        filename = f"{filename}.{os.path.splitext(target.filename)[1][1:]}"
    with open(filename, 'wb') as f:
        f.write(requests.get(target.url).content)
    return filename

def download_discord_attachments(targets, folder):
    if not os.path.isdir(folder):
        os.makedirs(folder)
    return [download_discord_attachment(t, folder + '/' + generate_uuid_from_msg(t.id), keep_ext = True) for t in targets]

async def prepare_VideoEdit(msg):
    targets = (await get_targets(msg, message_search_count = message_search_count)).compile()
    if not targets:
        await msg.channel.send("Unable to find a message to edit, maybe upload a video and try again?")
        return
    
    file_ext = os.path.splitext(targets[0].filename)[1][1:]
    if file_ext not in valid_extensions:
        await msg.channel.send(f"File type not valid, valid file types are: `{'`, `'.join(valid_extensions)}`")
        return
    
    return targets[0], f"{generate_uuid_folder_from_msg(msg.id)}.{file_ext}"

async def prepare_concat(msg, args):
    concat_count, *name_spec = args.split()
    try:
        concat_count = min(max_concat_count, max(2, (int(concat_count) if len(concat_count.strip()) else len(msg.attachments))))
    except Exception:
        await msg.reply(f'No video amount given, interpreting "{concat_count}" as specifier...')
        name_spec.insert(0, concat_count)
        concat_count = min(max_concat_count, max(2, len(name_spec)))
    
    targets_unsorted = list(filter(
        lambda t: os.path.splitext(t.filename)[1][1:] in valid_video_extensions,
        (await get_targets(msg, message_search_count = message_search_count)).compile()
    ))[:concat_count]
    
    targets = []
    for s in map(lambda c: c.strip().lower(), name_spec):
        i = 0
        while i < len(targets_unsorted):
            if targets_unsorted[i].filename.lower().startswith(s):
                targets.append(targets_unsorted.pop(i))
            i += 1
    targets += targets_unsorted
    
    if len(targets) < 2:
        await msg.reply("Unable to find enough videos to combine.")
        return
    
    return targets

def process_result_post(msg, res, prefix = None, random_message = True, filename = "video.mp4"):
    if res.success:
        text = random.choice(response_messages) if random_message else res.message
        content = f"{prefix} ║ {text}" if prefix else text
        messageQue.append(qued_msg(context = msg, filepath = res.filename, filename = filename, message = content, reply = True))
    else:
        messageQue.append(qued_msg(context = msg, message = res.message, reply = True))

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
    for command in commands: # scuffed way of processing commands
        spl = command.strip().split(' ', 1)
        cmd  = spl[0].strip().lower()
        args = spl[1].strip() if len(spl) > 1 else ""
        
        if cmd == "concat":
            Task(
                Action(prepare_concat, message, args,
                    name = "Concat Command Prep"
                ),
                Action(download_discord_attachments, swap_arg("result"), generate_uuid_folder_from_msg(message.id),
                    name = "Download videos to Concat"
                ),
                Action(combiner, swap_arg("result"), (concat_filename := f"{generate_uuid_folder_from_msg(message.id)}.mp4"),
                    SILENCE = "./editor/SILENCE.mp3",
                    print_info = False,
                    name = "Concat Videos",
                    fail_action = Action(
                        lambda n, e: messageQue.append(
                            qued_msg(
                                context = message,
                                message = "Sorry, something went wrong during concatenation.",
                                reply = True
                            )
                        )
                    )
                ),
                Action(process_result_post, message, result(True, concat_filename, ""), concat_filename,
                    name = "Post Concat"
                ),
                async_handler = async_runner
            ).run_threaded()
        elif cmd == "download":
            Task(
                Action(download, download_filename := f"{generate_uuid_folder_from_msg(message.id)}.mp4", args, name = "yt-dlp download"),
                Action(process_result_post, message, swap_arg("result"), download_filename, name = "Post Download"),
            ).run_threaded()
        elif (ev1 := (cmd in ["destroy", ""])) or has_meta_prefix:
            if not ev1 or cmd == "":
                args = f"{cmd} {args}"
            Task(
                Action(prepare_VideoEdit, message,
                    name = "VEB Command Prep",
                    check = lambda x: x is not None,
                    parse = lambda x: {
                        "target": x[0],
                        "filename": x[1]
                    }
                ),
                Action(download_discord_attachment, swap_arg("target"), swap_arg("filename"),
                    name = "VEB Download Target"
                ),
                Action(editor, swap_arg("filename"), args, workingDir = working_directory, keepExtraFiles = True,
                    name = "VEB",
                    parse = lambda x: {
                        "result": x,
                        "filename": x.filename
                    }
                ),
                Action(process_result_post, message, swap_arg("result"), swap_arg("filename"),
                    name = "VEB Post"
                ),
                async_handler = async_runner,
                persist_result_values = True
            ).run_threaded()
        

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
    asyncio.create_task(async_runner.looper())
    botReady = True
    info("Bot ready!")

@bot.event
async def on_message(msg):
    await parse_command(msg)

bot.run(discord_token)