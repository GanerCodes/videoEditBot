import os, json, discord
from editor import editor

config = json.load(open("config.json", 'r'))

bot = discord.AutoShardedClient(status = discord.Game(name = config["discordTagline"]), intents = intents)

bot.start(config["discordToken"])