import discord, asyncio, random, json, os
from concurrent.futures import ThreadPoolExecutor
from subprocessHelper import *
from pathHelper import *
from download import download
from autotune import *
from os import remove, path, makedirs
from re import sub

TOKEN = json.load(open("tokens.json"))["discord"]

messageCheckAmount = 10
dr = "files"
loglevel = "error"
exts = ["mp4", "webm", "mov", "mkv"]

if not path.isdir(dr):
	makedirs(dr)

bot = discord.AutoShardedClient()

@bot.event
async def on_ready():
	print("Bot ready.")

@bot.event
async def on_message(message):

	if (not message.guild) or (not message.channel.permissions_for(message.guild.me).send_messages): return

	if message.content.strip().lower() == "autotune help":
		await message.channel.send("""Bot usage:
	Autotune <link or search query> - Autotune a video (attached, replied to, or recent in channel) to another video.""")
	elif (s := message.content.strip().lower()).startswith("autotune"):
		attach = None
		if len(message.attachments) > 0:
			attach = message.attachments[0]
		elif message.reference and len(tmpDat := (await message.channel.fetch_message(message.reference.message_id)).attachments) > 0:
			attach = tmpDat[0]
		else:
			async for m in message.channel.history(limit = messageCheckAmount):
				if len(m.attachments) > 0:
					attach = m.attachments[0]
					break
		if attach:
			if getExt(attach.filename) in exts:
				if len(spl := sub(' +', ' ', message.content.strip()).split(' ', 1)) > 1:
					fileName = dr + '/discord_' + str(random.random()) + attach.filename
					await attach.save(fileName)
					loop = asyncio.get_event_loop()
					result = await loop.run_in_executor(ThreadPoolExecutor(), autotuneURL, fileName, spl[1])
					if type(result) == str:
						try:
							await message.channel.send("Autotuning go ETH! 0x013d1361177ab72b0cf096bd34fa671efb3eeeee", file = discord.File(result))
							remove(result)
						except Exception as e:
							print(e)
							await message.channel.send("Sorry, something went wrong uploading your video. Maybe the file is too large?")
					else: 
						await message.channel.send(result[0])
				else:
					await message.channel.send("Please send a link or search query")
			else:
				await message.channel.send("Invald file type, available formats: " + ', '.join(exts))
		else:
			await message.channel.send("Please attach a video to use autotune.")

print("Starting bot...")
bot.run(TOKEN)
