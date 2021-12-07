import os, json, discord
from editor import editor

config = json.load(open("config.json", 'r'))

intents = discord.Intents.default()
intents.messages = True
# intents.members = True
discord_status = discord.Game(name = config["discordTagline"])
bot = discord.AutoShardedClient(status = discord_status, intents = intents)
botReady = False

# download things >> destroy args
async def parse_command(msg):
    commands = msg.content.split(">>")[:2]
    for command in commands:
        spl = command.strip().split(' ', 1)
        cmd = spl[0].strip().lower()
        arg = spl[1].strip() if len(spl) == 2 else ""
        if cmd == "destroy":
            pass
        elif cmd == "concat":
            pass
        elif cmd == "download":
            pass
        await msg.channel.send(f"Got command: {cmd} | {arg}")

@bot.event
async def on_ready():
    global botReady
    if not botReady:
        botReady = True
        await bot.change_presence(activity = discord_status)
        print("Bot ready!")

@bot.event
async def on_message(msg):
    if msg.content.lower().strip().split(' ', 1)[0] in ("destroy", "copncat", "download"): #add alisases
        await parse_command(msg)

bot.run(config["discordToken"])