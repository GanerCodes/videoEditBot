import threading, requests, discord, asyncio, websockets, pickle, random, time, sys, psutil, os
from socketHelper import *
from pathHelper import chExt, cleanPath, tryToDeleteFile
from editor import videoEdit
from download import download
from getSens import getSens
from fixPrint import fixPrint

import logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

fixPrint("Starting renderer...")

IP_ADDR = getSens("host_ip")[0]
PORT = 6444
NAME = getSens("name")[0]
tmpDir = "TMPDIR"

VERBOSE_OUTPUT = False
w = None
isReady = False

botKey = None

messageQue = []
def processVideo(data): #Expecting: type, oldExt, url, channel, message
  global messageQue

  if VERBOSE_OUTPUT: fixPrint("ProcessVideo DATA:", data)

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
      if VERBOSE_OUTPUT:
        print("VEB_RESULT:", VEB_RESULT)
      if VEB_RESULT[0] == 0:
          if os.path.getsize(VEB_RESULT[1]) < 8 * 1024 ** 2:
              messageQue += [{"channel": data["channel"], "type": "file", "file": VEB_RESULT[1], "message": data["message"]}]
          else:
              messageQue += [{"channel": data["channel"], "type": "error", "message": f"Sorry, but the output file is too large."}]
              tryToDeleteFile(VEB_RESULT[1])
      else:
          msg = "Something went wrong editing your file, sorry." if len(VEB_RESULT) < 2 else ("Error: " + VEB_RESULT[1])
          messageQue += [{"channel": data["channel"], "type": "error", "message": msg}]
  elif data['type'] == 'download':
      fixPrint(f"Download - {data['url']}")
      if download(fileName := f"{tmpDir}/{uniqueID}.mp4", data['url'], duration = 110):
          messageQue += [{"channel": data["channel"], "type": "file", "message": data['message'], "file": fileName}]
      else:
          messageQue += [{"channel": data["channel"], "type": "error", "message": "Sorry, something went wrong downloading your video."}]
          tryToDeleteFile(fileName)

async def videoEditBotClient():
    global VERBOSE_OUTPUT, botKey, w
    while True:
        try:
            try:
                w = await websockets.connect(f"ws://{IP_ADDR}:{PORT}")
            except Exception as e:
                raise Exception(f"Error connecting to server; {e}")
            fixPrint("Connected to server.")
            try:
                while True:
                    data = await w.recv()
                    try:
                        data = pickle.loads(data)
                    except Exception as e2:
                        raise Exception(f"Error unpickling; {e2}")
                    if VERBOSE_OUTPUT: fixPrint(f"|||{data}")
                    if type(data) == str: #Check if got string
                        if data == "getName":
                            await w.send(pickle.dumps({'type': 'name', 'name': NAME}))
                            fixPrint(f"Sent name ({NAME})")
                        elif data == "verbose_veb_on":
                            fixPrint("Verbose output set to:", VERBOSE_OUTPUT := True)
                        elif data == "verbose_veb_off":
                            fixPrint("Verbose output set to:", VERBOSE_OUTPUT := False)
                        elif data == "restart":
                            await w.close()
                            psutil.Process(os.getpid()).terminate()
                    elif type(data) == dict: #Check if dictionary
                        if data['type'] in ['edit', 'download']:
                            threading.Thread(target = processVideo, args = [data]).start()
                        elif data['type'] == "key":
                            if botKey != None and data['key'] != botKey:
                                await w.close()
                                psutil.Process(os.getpid()).terminate()
                            else:
                                botKey = data['key']
                                if isReady:
                                    await w.send(pickle.dumps({'type': 'ready'}))
            except Exception as e:
                await w.close()
                raise Exception(f"SOme shit went wack, error: {e}")
        except Exception as err:
            fixPrint(f"Error; {err}")
        time.sleep(1)
def editor():
    asyncio.new_event_loop().run_until_complete(videoEditBotClient())
threading.Thread(target = editor).start()

async def queMessages():
    global messageQue
    while True:
        while len(messageQue) > 0:
            try:
                msg = messageQue.pop()
                if VERBOSE_OUTPUT: fixPrint("QueMessages:", msg)
                channel = await bot.fetch_channel(msg['channel'])
                if not channel:
                    fixPrint("Error getting channel", msg['channel'])
                    if msg['type'] == "file":
                        tryToDeleteFile(msg['file'])
                    continue
                if msg['type'] == "file":
                    try: 
                        await channel.send(msg['message'] + f' [{NAME}]', files = [discord.File(msg['file'])])
                    except Exception as e: 
                        fixPrint("Couldn't send file.", e)
                    tryToDeleteFile(msg['file'])
                elif msg['type'] == "error":
                    await channel.send(msg['message'] + f' [{NAME}]')
            except Exception as e:
                print("Error in queMessages()!:", e)
            await asyncio.sleep(0.1)
        await asyncio.sleep(0.5)



while botKey == None: pass

bot = discord.AutoShardedClient(intents = discord.Intents())

@bot.event
async def on_ready():
    global isReady, w
    print("ON_READY() TRIGGERED")
    if not isReady:
        isReady = True
        await w.send(pickle.dumps({'type': 'ready'}))
        fixPrint("Sent ready.")
        await bot.loop.create_task(queMessages())

bot.run(botKey)