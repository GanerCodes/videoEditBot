import tweepy, shutil, datetime, time, subprocess, requests, threading, random, re, os
from imageCorrupt import imageCorrupt
from destroyer import videoEdit
from threadQue import *
from fixPrint import fixPrint
from getSens import getSens
from random import randrange as r, choice as rc
from PIL import Image
Thread = threading.Thread


DIRECTORY = f"{getSens('dir')[0]}"
BASEURL = getSens('website')[0]


if not os.path.isdir(DIRECTORY):
    os.makedirs(DIRECTORY)
    os.makedirs(f"{DIRECTORY}/@")
    print(f'Created directory "{DIRECTORY}" and "{DIRECTORY}/@"')

que = threadQue(l = True)

consumer_key, consumer_secret, access_key, access_secret = getSens("consumer_key", "consumer_secret", "access_key", "access_secret")

def makeApi(access_key, access_secret):
	authorization = tweepy.OAuthHandler(consumer_key, consumer_secret)
	authorization.set_access_token(access_key, access_secret) 
	return tweepy.API(authorization)

api = makeApi(access_key, access_secret)

if all(altKeys := getSens("alt_access_key", "alt_access_secret")):
	altAPI = makeApi(*altKeys)
else:
	altAPI = api

currentTweet, lastTweet = None, None

def testCode(c):
	if type(c) == int:
		if c == 185:
			return "Error: Rate limit."
		elif c == 385:
			return "Error: Can't see tweet to reply to."
		else:
			return False
	else:
		if c.api_code is not None:
			return testCode(c.api_code)
		else:
			return f"NON-TWITTER API ERROR {str(c)}"

def UFID(ID, l):
	random.seed(ID)
	return ''.join([str(random.randint(0, 9)) for i in range(l)])

def formatPrint(pre, msg):
	tab, nlin = '\t', '\n'
	fixPrint(f"{pre}:{tab*2}{msg.replace(nlin, '')}")

def botPrint(*objs, prefix = "", **kobjs):
	formatPrint(prefix, ' '.join(map(str, objs)))

def prettyRun(pre, cmd):
    proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, universal_newlines = True)
    while proc.poll() is None:
        out = proc.stdout.readline()
        if out != "":
            formatPrint(pre, out)
    return proc.returncode

def getContent(m, ID, tweet, uniquePrefix, reply, isRetweet):
	name = ""
	mediaType = "mp4"

	if tweet._json['extended_entities']['media'][0]['type'] == 'animated_gif' or m['expanded_url'].split('/')[-2] == "video": #Check if GIF or normal video
		name = f"{uniquePrefix}_{ID}.mp4"
		subprocess.check_output(["youtube-dl", "--quiet", "--no-playlist", "--geo-bypass", "--merge-output-format", "mp4", "-r", "5M", "-o", f"{uniquePrefix}_{ID}.mp4", f"{m['expanded_url']}"])
	else: #Check if image
		mediaType = "png"
		TExt = m['media_url'].split('.')[-1]
		name = f'''{uniquePrefix}_{ID}.{TExt}'''
		if TExt == "jpg":
			mediaType = "png"
		with open(name, 'wb') as f:
			f.write(requests.get(m['media_url']).content)

	tt = reply._json['full_text']
	#print("Tweet text: ", tt)
	txt = re.split("@videoeditbot", tt, flags=re.IGNORECASE)[-1].strip()
	for i in tweet._json['entities']['media']:
		txt = txt.replace(i['url'], "")
	if isRetweet:
		txt = re.sub(r"https:\/\/t.co\/\S{1,30}$", '', txt)
	if 'tovid' in txt.lower():
		mediaType = "mp4"

	j = txt.strip().replace(' ', '').replace('\n', '')
	
	prefix = f"P-{UFID(ID, 3)}"
	def bpnt(m):
		print(f"{prefix}:\t\t{m}")


	tt = tmpName if (tmpName := '@'+reply._json['user']['screen_name']) != '@videoeditbot' else ""
	now = datetime.datetime.now()
	millis = str(int(round(time.time() * 1000)))
	folder = DIRECTORY
	foldName = reply._json['user']['screen_name'].lower()
	newFolder = f"{folder}/{foldName}"
	finalName = f"{uniquePrefix}_{ID}.{mediaType}"
	fileName = f"_{foldName}_{millis}_{finalName[-6:]}"
	newLocation = f"{newFolder}/{fileName}"
	newURL = f"{BASEURL}/{foldName}/{fileName}?video"


	arguments = None
	if len(j) < 7 and re.match(r"i\|[0-9]{1,3}", j):
		ret = imageCorrupt(name, j.split('|')[-1])
	else:
		def altPrint(*args, **kwargs):
			botPrint(*args, prefix = prefix, **kwargs)
		isRandom = re.sub(r"@[^ ]{1,}", '', txt).strip() in ['random', 'r', 'rnadom', '']
		ret = videoEdit(name, txt, disallowTimecodeBreak = True, fixPrint = altPrint, durationUnder = 142, allowRandom = isRandom)
		if ret == -1:
			#bpnt("Not a tweet with arguments, ignoring.")
			if os.path.isfile(finalName): #Delete downloaded file
				os.remove(finalName)
			return

	#Codes:
	# -1: could not tweet text based reply
	# 0 : told the user that there was an error
	# 1 : send text based reply with link, but reasoning was not handled (ex. duration, aspect ratio, etc.)
	# 2 : sucessfully uploaded video to twitter

	def backup():
		thumbFold = f"{newFolder}/thumb"
		if os.path.isdir(thumbFold) is not True:
			os.makedirs(thumbFold)
		shutil.move(finalName, newLocation)
		if mediaType == "mp4":
			thumbLoc = f"{thumbFold}/{os.path.splitext(fileName)[0]}.jpg"
			subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", newLocation, "-vframes", "1", thumbLoc])
			# os.system(f"ffmpeg -hide_banner -loglevel fatal -i '{newLocation}' -vframes 1 '{thumbLoc}'")
			img = Image.open(thumbLoc)
			img.thumbnail((250, 250))
			img.save(thumbLoc)

	replyApi = api#random.choice(apilist)

	#Respond if error code in destroyer result
	try:
		code = ret[0]
		if code > 0:
			if os.path.isfile(finalName): #If the file is still there, remove it
				os.remove(finalName)
			if len(ret) > 1:
				responce = ret[1]
			else:
				responce = "Unhandled error."
			replyApi.update_status(f"{tt} Sorry, something went wrong editing your video. Error: {responce}", in_reply_to_status_id = str(reply.id), auto_populate_reply_metadata=True)
			bpnt("Tweet posted (0) (Handled)")
			return
	except Exception as e:
		if (tc := testCode(e)):
			bpnt(tc)
			return
		bpnt(e)


	#Check if video exists
	try:
		backup()
	except Exception as e:
		try:
			replyApi.update_status(f"{tt} Something went wrong processing your edit, inform Ganer if this is a mistake.", in_reply_to_status_id = str(reply.id), auto_populate_reply_metadata=True)
			bpnt("Can't find result! Error tweet sent.")
		except Exception as b:
			bpnt("Can't find result! Error code: "+str(b.api_code))
		return

	#Try and upload the video
	try:
		fsize = os.path.getsize(newLocation) / (1024 ** 2)
		if fsize > 15.3:
			replyApi.update_status(f"Your video was too large to upload directly, here is a backup of the result: {newURL}", in_reply_to_status_id = str(reply.id), auto_populate_reply_metadata=True)
			bpnt("Tweet posted (2)")
		else:
			mediaID = replyApi.media_upload(newLocation)
			time.sleep(5)
			replyApi.update_status('', media_ids=[mediaID.media_id_string], in_reply_to_status_id = str(reply.id), auto_populate_reply_metadata=True)
			bpnt("Tweet posted (2)")
			return

	#If that failed
	except Exception as e:
		if (tc := testCode(e)):
			bpnt(tc)
			return
		try:
			code = e.api_code
			errorMessage = f"Something went wrong, Twitter error code {code}"

			replyApi.update_status(f"{errorMessage}, here is a backup of the result: {newURL}", in_reply_to_status_id = str(reply.id), auto_populate_reply_metadata=True)
			bpnt(f"Tweet posted (1), Twitter error code: {code}")
			return
		except Exception as b:
			bpnt(f"WARN (-1) Code: {b.api_code}")

def callBot(e, ID, mostRecentTweet, uniquePrefix, reply, isRetweet = False):
	global count
	if 'media' in e:
		m = e['media'][0]
		try:
			folder = DIRECTORY
			foldName = reply._json['user']['screen_name']
			if os.path.isdir(f"{folder}/{foldName}") is not True:
				os.makedirs(f"{folder}/{foldName}")
			que.addThread(dummyThread(target = getContent, args = [m, ID, mostRecentTweet, uniquePrefix, reply, isRetweet]))
			count += 1
		except Exception as e:
			print("Error!", e)
	else:
		pass #if you want you can make it do something if there isn't media in the tweet/retweet/reply

def getID(obj):
	return obj._json['id']
def getIDlist(ls):
	return [getID(i) for i in ls]

myId = api.me().id

mostRecentID = None
while True:
	try:
		mostRecentID = getID(list(api.mentions_timeline(count = 1, tweet_mode = 'extended'))[0])
		break
	except Exception as e:
		print("Error getting most recent tweet, waiting 15 seconds to retry.")
		time.sleep(15)

ignoreList = [mostRecentID]
print("Started, saved ID", mostRecentID, "into ignore list.")

count = 0

while True:
	time.sleep(20)
	mentionsList = None
	try:
		mentionsList = list(api.mentions_timeline(since_id = mostRecentID, count = 10, tweet_mode = 'extended'))
		if len(mentionsList) > 0:
			pass
		else: #No new tweets
			continue
	except Exception as e:
		if (cod := testCode(e)):
			print("Error getting timeline,", cod)
		else:
			print("Error getting tweets:", e)
		time.sleep(10)
		continue
	if len(mentionsList) > 0:
		mostRecentID = getID(mentionsList[0])
       
	activeList = [i for i in mentionsList if getID(i) not in ignoreList]
	ignoreList.extend(getIDlist(activeList))
	#ignoreList = ignoreList[-5:]

	if len(activeList) > 0:
		pass
	else:
		continue #Found no tweets suited to be process.
	n = 0
	count = 0
	for mostRecentTweet in activeList:
		n += 1
		e = mostRecentTweet._json['entities']
		ID = getID(mostRecentTweet)
		uniquePrefix = ''.join([str(r(0, 10)) for i in range(6)])
		if 'media' in e:
			callBot(e	, ID		, mostRecentTweet, uniquePrefix, mostRecentTweet)
		elif mostRecentTweet._json['in_reply_to_status_id_str'] is not None:
			try:
				topUser = altAPI.get_status(mostRecentTweet._json['in_reply_to_status_id_str'], tweet_mode = 'extended')
			except tweepy.TweepError as TE:
				if (codeMsg := testCode(TE)):
					print(codeMsg)
					pass
				else:
					try:
						api.update_status(f"I can't see tweet you replied to. Perhaps they have the bot blocked or a private account?", in_reply_to_status_id = mostRecentTweet.id, auto_populate_reply_metadata=True)
					except Exception as aex:
						if (codeMsg := testCode(aex)):
							print(codeMsg)
							pass
						else:
							print("grp", aex)
				continue

			topUserE = topUser._json['entities']
			topTweetTagCount = (topUser._json['full_text'].lower()+'@'+topUser._json['user']['screen_name']).count("@videoeditbot")
			tagCount = mostRecentTweet._json['full_text'].lower().count("@videoeditbot")
			isReplyToMyTweet = (not topUser._json['in_reply_to_status_id_str']) and topUser._json['user']['screen_name'] == "@videoeditbot"
			if topTweetTagCount > 0 and not isReplyToMyTweet:
				if tagCount < 2:
					continue
			if tagCount > 0 or isReplyToMyTweet:
				callBot(topUserE, topUser._json['id'], topUser, uniquePrefix, mostRecentTweet)
			
		else:
			try:
				topUser = altAPI.get_status(mostRecentTweet._json['quoted_status_id_str'], tweet_mode = 'extended')
				topUserE = topUser._json['entities']
				callBot(topUserE, topUser._json['id'], topUser, uniquePrefix, mostRecentTweet, isRetweet = True)
			except Exception as e:
				continue
	que.runQuedThreads()
	if count > 0:
		print(f"Executed destroyer for {count} tweet(s); {str(que).lower()}.")