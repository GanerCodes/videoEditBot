import os, json, discord
from editor import editor

editor("hi.mp4", "pitch 25, autotune, vol 2, sfx", "./active")

config = json.load(open("config.json", 'r'))

intents = discord.Intents.default()
intents.messages = True
#intents.members = True
discord_status = discord.Game(name = config["discordTagline"])
bot = discord.AutoShardedClient(status = discord_status, intents = intents)
botReady = False

@bot.event
async def on_ready():
    if not botReady:
        botReady = True
        await bot.change_presence(activity = discord_status)
        print("Bot ready!")

# bot.start(config["discordToken"])