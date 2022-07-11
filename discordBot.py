# TODO: every 5 minutes scan, with another bot, update the donor guilds/users.
# Check owner of guild when processing command, apply relevent donor perks

import os, sys, time, random, discord, requests, asyncio, logging
from pyjson5 import load as json_load
from combiner import combiner
from editor.download import download
from collections import namedtuple, defaultdict
from func_helper import  *
from threading import Thread
from functools import reduce
from operator import add
from editor import editor
from math import ceil

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_handler = logging.StreamHandler(sys.stdout)
logger_handler.setLevel(logging.DEBUG)
logger.addHandler(logger_handler)
info = lambda *args: logger.info(' | '.join(map(str, args)))

config = json_load(open("config.json", 'r'))

message_search_count = config["message_search_count"]
command_chain_limit  = config["command_chain_limit"]
working_directory    = os.path.realpath(config["working_directory"])
response_messages    = config["response_messages"]
max_concat_count     = config["max_concat_count"]
discord_tagline      = config["discord_tagline"]
discord_token        = config["discord_token"]
meta_prefixes        = config["meta_prefixes"]
cookie_file          = config["cookie_file"] if "cookie_file" in config else None
donor_guild_id       = config["donor_guild_id"] if "donor_guild_id" in config else None

donor_teir_roles = config["donor_teir_roles"] if donor_guild_id else None
donor_guild_check_seconds = config["donor_guild_check_seconds"] if donor_guild_id else None

valid_video_extensions = ["mp4", "webm", "avi", "mkv", "mov"]
valid_image_extensions = ["png", "gif", "jpg", "jpeg"]
valid_extensions = valid_video_extensions + valid_image_extensions

get_default = lambda v, d = config["unspecified_default_timeout"]: v["default"] if "default" in v else d
def config_timeout(default, custom):
    default_timeout = get_default(default)
    return defaultdict(
        lambda: defaultdict(
            lambda: default_timeout, **default
        ), **{
            k: defaultdict(
                lambda: get_default(v, default_timeout), **v
            ) for k, v in custom.items()
        }
    )

guild_timeout_durations = config_timeout(config["default_guild_timeouts"], config["custom_guild_timeouts"])
user_timeout_durations = config_timeout(config["default_user_timeouts"], config["custom_user_timeouts"])
guild_timeouts = defaultdict(lambda: 0)
user_timeouts  = defaultdict(lambda: 0)

qued_msg = namedtuple("qued_msg", "context message filepath filename reply edit", defaults = 6 * [None])
result = namedtuple("result", "success filename message", defaults = 3 * [None])

async_runner = Async_handler()
taskList, messageQue = [], []

intents = discord.Intents.default()
intents.messages = True
intents.members = True
discord_status = discord.Game(name = discord_tagline)
bot = discord.AutoShardedClient(status = discord_status, intents = intents)

class target_group:
    def __init__(self, attachments, reply, channel):
        self.attachments = attachments
        self.reply       = reply
        self.channel     = channel
    def compile(self):
        k = []; [k.append(i) for i in (self.attachments + self.reply + self.channel) if i not in k]
        return k

def human_size(size, units=[' bytes','KB','MB','GB','TB', 'PB', 'EB']): # https://stackoverflow.com/a/43750422/14501641
    return str(size) + units[0] if size < 1024 else human_size(size >> 10, units[1:])

def generate_uuid_from_msg(msg_id):
    return f"{msg_id}_{(time.time_ns() // 100) % 1000000}"

def generate_uuid_folder_from_msg(msg_id):
    return f"{working_directory}/{generate_uuid_from_msg(msg_id)}"

def clean_message(msg):
    return msg.replace(chr(8206), '').replace('@', '@'+chr(8206))

def apply_timeouts(msg, command,
        guild_timeout_durations = guild_timeout_durations,
        user_timeout_durations = user_timeout_durations,
        guild_timeouts = guild_timeouts,
        user_timeouts = user_timeouts):
        
    
    ahr_id = str(msg.author.id)
    try:
        gld_id = str(msg.guild.id )
        try:
            gld_own_id = str(msg.guild.owner.id)
        except AttributeError:
            gld_own_id = '0'
            print(f"Error aquiring owner ID for guild ID {gld_id}")
    except AttributeError:
        gld_id = "0"
        print(f"Error aquiring guild ID for author ID {ahr_id}")
    
    if "ghost" in user_timeout_durations[ahr_id] or "ghost" in guild_timeout_durations[gld_id]:
        return True
    
    gt, ut = guild_timeouts[gld_id], user_timeouts[ahr_id]
    is_donor_user = "donor" in user_timeout_durations[ahr_id]
    is_donor_guild = "donor" in user_timeout_durations[gld_own_id]
    
    ct = time.time()
    if not is_donor_user and ct < gt:
        return gt - ct
    if ct < ut:
        return ut - ct
    
    user_timeouts[ahr_id] = ct + user_timeout_durations[ahr_id][command] * (
        user_timeout_durations[ahr_id]["user_timeout_multiplier"] if is_donor_user else 1)
    if not is_donor_user:
        guild_timeouts[gld_id] = ct + guild_timeout_durations[gld_id][command] * (
            user_timeout_durations[gld_own_id]["guild_timeout_multiplier"] if is_donor_guild else 1)
    
    return True

async def check_donors():
    global guild_timeout_durations, user_timeout_durations
    
    donor_guild = bot.get_guild(int(donor_guild_id))
    count = 0
    while True:
        if not donor_guild:
            print("Unable to get donor guild! Retrying in 10 seconds.")
            await asyncio.sleep(10)
            donor_guild = bot.get_guild(donor_guild_id)
            continue
        
        new_users = {}
        for role_id, perks in donor_teir_roles.items(): # Iterate donor roles
            discord_role = donor_guild.get_role(int(role_id))
            user_perks, guild_perks = perks["user"], perks["guild"]
            for member in discord_role.members: # Iterate donors in role
                if (mem_id := str(member.id)) in config["custom_user_timeouts"]: # User has custom override 
                    continue
                
                new_users[mem_id] = {
                    "donor": True,
                    "user_timeout_multiplier": user_perks["timeout_multiplier"],
                    "max_chain": user_perks["max_chain"],
                    "guild_timeout_multiplier": guild_perks["timeout_multiplier"],
                    "guild_max_chain": guild_perks["max_chain"]
                } | config["default_user_timeouts"]
        
        if count == 0:
            print(f"Found {len(new_users)} donators!")
        
        user_timeout_durations = config_timeout(config["default_user_timeouts"], config["custom_user_timeouts"] | new_users)
        await asyncio.sleep(donor_guild_check_seconds)
        count += 1

async def processQue():
    while True:
        if not len(messageQue):
            await asyncio.sleep(1)
            continue
            
        res = messageQue.pop(0)
        
        action = res.context.reply if res.reply else (res.context.edit if res.edit else res.context.channel.send)
        if res.filename:
            if (filesize := os.path.getsize(res.filename)) >= 8 * 1024 ** 2:
                await action(f"Sorry, but the resulting file ({human_size(filesize)}) is over Discord's 8MB upload limit.")
            else:
                with open(res.filename, 'rb') as f:
                    args = [res.message] if res.message else []
                    file_kwargs = {"filename": res.filename} if res.filename else {}
                    if res.message and res.context.content.startswith('!') and (action == res.context.reply and res.context.author.id == bot.user.id):
                        await res.context.delete()
                        await asyncio.sleep(1)
                        await res.context.channel.send(*args, file = discord.File(f, **file_kwargs))
                    else:
                        await action(*args, file = discord.File(f, **file_kwargs))
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
    concat_count, *name_spec = params if len(params := args.split()) else '2'
    try:
        concat_count = min(max_concat_count, max(2, (int(concat_count) if len(concat_count.strip()) else len(msg.attachments))))
    except Exception as err:
        await msg.reply(f'No video amount given, interpreting "{concat_count}" as specifier...')
        name_spec.insert(0, concat_count)
        concat_count = min(max_concat_count, max(2, len(name_spec)))
    
    targets_unsorted = list(filter(
        lambda t: os.path.splitext(t.filename)[1][1:] in valid_video_extensions,
        (await get_targets(msg, message_search_count = message_search_count, stop_on_first = False)).compile()
    ))[:concat_count]
    
    if len(targets_unsorted) < 2:
        await msg.reply("Unable to find enough videos to combine.")
        return
    
    targets = []
    for s in map(lambda c: c.strip().lower(), name_spec):
        i = 0
        while i < len(targets_unsorted):
            if targets_unsorted[i].filename.lower().startswith(s):
                targets.append(targets_unsorted.pop(i))
            i += 1
    targets += targets_unsorted
    
    return targets

def process_result_post(msg, res, filename = "video.mp4", prefix = None, random_message = True):
    if res.success:
        text = random.choice(response_messages) if random_message else res.message
        content = f"{prefix.strip()} ║ {text.strip()}" if prefix else text.strip()
        messageQue.append(qued_msg(context = msg, filepath = res.filename, filename = filename, message = content, reply = True))
    else:
        messageQue.append(qued_msg(context = msg, message = res.message, reply = True))

async def parse_command(message):
    if message.author.id == bot.user.id and not '║' in message.content:
        return
    
    msg = message.content.split('║', 1)[0]
    if len(msg) == 0: return
    
    is_reply_to_bot = message.reference and (await message.channel.fetch_message(message.reference.message_id)).author.id == bot.user.id

    if message.author.id != bot.user.id and not is_reply_to_bot and msg.split('>>')[0].removeprefix('!').strip() == "":
        return
    
    has_meta_prefix = is_reply_to_bot
    append_space = ' ' if ' ' in msg else ''
    for pre in meta_prefixes:
        if msg.startswith(pre + append_space):
            has_meta_prefix = True
            msg = msg.removeprefix(pre).lstrip()
            break
    
    cmd_name_opts = ["concat", "combine", "download", "downloader", "destroy"]
    
    author_id = str(message.author.id)
    
    chain_limit = 9999 if message.author.id == bot.user.id else (
        user_timeout_durations[author_id]["max_chain"] if (
            author_id in user_timeout_durations and "max_chain" in user_timeout_durations[author_id]
        ) else command_chain_limit
    )
    
    command, *remainder = msg.split(">>")[:chain_limit]
    if command.startswith('!'):
        command = command.removeprefix('!')
    
    remainder = clean_message('>>'.join(remainder)).strip()
    
    if len(remainder) and not any(remainder.removeprefix('!').startswith(i) for i in cmd_name_opts):
        remainder = f"destroy {remainder}"
    
    spl = command.strip().split(' ', 1)
    cmd  = spl[0].strip().lower()
    args = spl[1].strip() if len(spl) > 1 else ""
    
    final_command_name = None
    if cmd in ["concat", "combine"]:
        final_command_name = "concat"
    elif cmd in ["download", "downloader"]:
        final_command_name = "download"
    elif cmd == "help":
        final_command_name = "help"
    elif cmd == "hat":
        final_command_name = "hat"
    elif (ev1 := (cmd in ["destroy", ""])) or has_meta_prefix:
        final_command_name = "destroy"
        if not ev1 or cmd == "":
            args = f"{cmd} {args}"

    if not final_command_name:
        return

    is_timeout = apply_timeouts(message, cmd, guild_timeout_durations, user_timeout_durations, guild_timeouts, user_timeouts)
    if is_timeout is not True:
        await message.reply(f"Please wait {ceil(is_timeout)} seconds to use this command again.")
        return

    match final_command_name:
        case "help":
            await message.reply("VideoEditBot Command Documentation: https://github.com/GanerCodes/videoEditBot/blob/master/COMMANDS.md")
        case "hat":
            embed = discord.Embed(title = 'hat', description = 'hat')
            embed.set_image(url = "https://cdn.discordapp.com/attachments/748021401016860682/920801735147139142/5298188282_1639606638167.png")
            await message.reply("Hat", embed=embed)
        case "concat":
            Task(
                Action(prepare_concat, message, args,
                    name = "Concat Command Prep",
                    check = lambda x: x
                ),
                Action(download_discord_attachments, swap_arg("result"), generate_uuid_folder_from_msg(message.id),
                    name = "Download videos to Concat",
                    check = lambda x: x
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
                Action(process_result_post, message, result(True, concat_filename, ""), concat_filename, remainder,
                    name = "Post Concat"
                ),
                async_handler = async_runner
            ).run_threaded()
        case "download":
            Task(
                Action(download, download_filename := f"{generate_uuid_folder_from_msg(message.id)}.mp4", args, name = "yt-dlp download"),
                Action(process_result_post, message, swap_arg("result"), download_filename, remainder,
                    name = "Post Download"
                ),
            ).run_threaded()
        case "destroy":
            Task(
                Action(prepare_VideoEdit, message,
                    name = "VEB Command Prep",
                    check = lambda x: x,
                    parse = lambda x: {
                        "target": x[0],
                        "filename": x[1]
                    },
                    skip_task_fail_handler = True
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
                Action(process_result_post, message, swap_arg("result"), swap_arg("filename"), remainder,
                    name = "VEB Post"
                ),
                async_handler = async_runner,
                persist_result_values = True
            ).run_threaded()
            
botReady = False
@bot.event
async def on_ready():
    global botReady, meta_prefixes
    if botReady: pass
    
    meta_prefixes += [
         f"<@{bot.user.id}>",
        f"<@!{bot.user.id}>",
        f"<@&{bot.user.id}>",
        f"<@#{bot.user.id}>",
    ]
    if not os.path.isdir(working_directory):
        os.makedirs(working_directory)
    
    await bot.change_presence(activity = discord_status)
    if donor_guild_id:
        asyncio.create_task(check_donors())
    asyncio.create_task(processQue())
    asyncio.create_task(async_runner.looper())
    
    botReady = True
    info("Bot ready!")

@bot.event
async def on_message(msg):
    await parse_command(msg)

bot.run(discord_token)