import threading, requests, discord, socket, pickle, random, time, os
from socketHelper import *
from pathHelper import chExt, cleanPath, tryToDeleteFile
from destroyer import videoEdit
from download import download
from getSens import getSens

tmpDir = "tmpFiles"

UNIQUE_ID, hostAddress = getSens("name", "host_ip")
messageQue = []
hasStarted = False
s = None

async def queMessages():
	global messageQue
	while True:
		while len(messageQue) > 0:
			msg = messageQue.pop()
			channel = await bot.fetch_channel(msg['channel'])
			if not channel:
				print("Error getting channel", msg['channel'])
				if msg['type'] == "file":
					tryToDeleteFile(msg['file'])
				continue
			if msg['type'] == "file":
				try: 
					await channel.send(msg['message'] + f' [{UNIQUE_ID}]', files = [discord.File(msg['file'])])
				except Exception as e: 
					print("Couldn't send file.", e)
				tryToDeleteFile(msg['file'])
			elif msg['type'] == "error":
				await channel.send(msg['message'] + f' [{UNIQUE_ID}]')

def processVideo(data, s):
	global messageQue

	millis = str(int(round(time.time() * 1000)))
	uniqueID = f"{''.join([str(random.randint(0, 9)) for i in range(10)])}_{millis}"
	if not os.path.isdir(tmpDir): os.makedirs(tmpDir)

	if data['type'] == 'edit':
		newFile = cleanPath(f"{tmpDir}/{uniqueID}.{data['oldExt']}")
		try:
			with open(newFile, "wb") as f:
				f.write(requests.get(data['url'], allow_redirects = True).content)
		except:
			messageQue += [{"channel": data["channel"], "type": "error", "message": "There was an error while downloading your file."}]
			return

		VEB_RESULT = videoEdit(newFile, data['args'], durationUnder = 120, logErrors = True)
		if VEB_RESULT[0] == 0:
			if os.path.getsize(VEB_RESULT[1]) < 8 * 1024 ** 2:
				messageQue += [{"channel": data["channel"], "type": "file", "file": VEB_RESULT[1], "message": data["message"]}]
			else:
				messageQue += [{"channel": data["channel"], "type": "error", "message": f"Output file is > {8 * 1024 ** 2} Bytes, a solution will be found soon."}]
				tryToDeleteFile(VEB_RESULT[1])
				# SWHAP({'type': 'file', 'file': open(VEB_RESULT[1], "rb").read()}, s)
		else:
			msg = "Something went wrong editing your file, sorry." if len(VEB_RESULT) < 2 else ("Error: " + VEB_RESULT[1])
			messageQue += [{"channel": data["channel"], "type": "error", "message": msg}]
	elif data['type'] == 'download':
		print(f"Download - {data['url']}")
		if download(fileName := f"{tmpDir}/{uniqueID}.mp4", data['url'], duration = 110):
			messageQue += [{"channel": data["channel"], "type": "file", "message": data['message'], "file": fileName}]
		else:
			messageQue += [{"channel": data["channel"], "type": "error", "message": "Sorry, something went wrong downloading your video."}]
			tryToDeleteFile(fileName)

disconnected = False
token = None
run = None
bot = discord.AutoShardedClient(intents = discord.Intents())

def connect():
	global s
	try: s.close()
	except: pass

	try:
		s = socket.socket()
		s.connect((hostAddress, 6444))
		return True
	except:
		print("Couldn't connect to server.")
		return False

def disconnectFix():
	global disconnected, hasStarted, s
	if connect():
		SWHAP({'type': 'ID', 'ID': UNIQUE_ID}, s)
		print("Sending ID", UNIQUE_ID)
		if hasStarted:
			SWHAP({'type': 'ready'}, s)
			print("Sending ready.")
		disconnected = False
	else:
		disconnected = True

def client():
	global disconnected, hasStarted, token, bot, run, s
	while True:
		connect()
		try:
			while True:
				if (data := receiveWithHeader(s)) != -1 and data:
					if "GET_ID" in data:
						print("Got token; returning ID", UNIQUE_ID)
						SWHAP({'type': 'ID', 'ID': UNIQUE_ID}, s)
						if data['token'] != token:
							token = data['token']
							run = True
						if hasStarted:
							SWHAP({'type': 'ready'}, s)
							print("Sent ready.")

					elif 'type' in data:
						threading.Thread(target = processVideo, args = [data, s]).start()
				else:
					raise Exception("Couldn't receive data, disconnected.")

		except Exception as e:
			print("Unable to connect to server:", e)
			disconnected = True
			time.sleep(3)

threading.Thread(target = client).start()

while not token: pass #Wait until got discord token

def pingCheck():
	global disconnected, run, s
	while True:
		try:
			SWHAP('p', s)
		except Exception as e:
			print("Disconnect:", e)
			disconnected = True

		if disconnected: 
			print("Disconnected, retrying.")
			disconnectFix()
		time.sleep(5)
threading.Thread(target = pingCheck).start()

@bot.event
async def on_ready():
	global disconnected, hasStarted

	if not hasStarted:
		hasStarted = True
		print("Discord bot ready.")
		try:
			SWHAP({'type': 'ready'}, s)
			print("Sent ready.")
		except:
			print("Couldn't send ready info.")
			disconnected = True
			pass
		await bot.loop.create_task(queMessages())

print("Starting bot.")
bot.run(token)