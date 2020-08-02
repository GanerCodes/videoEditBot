import tweepy, datetime, time, subprocess, requests, threading, random, re, os
from random import randrange as r

DIRECTORY = "C:/Network_folder/Public/Twitter"



def formatKey(l):
	return l.split('=')[1].strip().replace('"', '')

consumer_key, consumer_secret, access_key, access_secret = "", "", "", ""
with open("TOKENS.txt") as f:
	for line in f:
		ll = line.lower()
		if "consumer_key" in ll:
			consumer_key = 		formatKey(line)
		elif "consumer_secret" in ll:
			consumer_secret =	formatKey(line)
		elif "access_key" in ll:
			access_key =		formatKey(line)
		elif "access_secret" in ll:
			access_secret =		formatKey(line)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret) 
api = tweepy.API(auth) 

currentTweet, lastTweet = None, None

def UFID(ID, l):
	random.seed(ID)
	return ''.join([str(random.randint(0, 9)) for i in range(l)])

def prettyRun(pre, cmd):
    tab, nlin = '\t', '\n'
    proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, universal_newlines = True)
    while proc.poll() is None:
        out = proc.stdout.readline()
        if out != "":
            print(f"{pre}:{tab*2}{out.replace(nlin, '')}")
    return proc.returncode

def getContent(m, ID, tweet, uniquePrefix, reply, isRetweet):
	name = ""
	mediaType = "mp4"

	isGif = tweet._json['extended_entities']['media'][0]['type'] == 'animated_gif'

	if isGif or m['expanded_url'].split('/')[-2] == "video":
		name = f"{uniquePrefix}_{ID}.mp4"
		subprocess.call(f'''youtube-dl --quiet --no-playlist --geo-bypass --max-filesize 50M --merge-output-format mp4 -r 5M -o {uniquePrefix}_{ID}.mp4 "{m['expanded_url']}"''')
	else:
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
	#print(f'Formatted tweet text: "{txt}"')

	j = txt.strip().replace(' ', '').replace('\n', '')
	arguments = None

	if len(j) < 7 and re.match(r"i\|[0-9]{1,3}", j):
		arguments = ["python", "-u", "imageCorrupt.py", j.split('|')[-1], name]
	else:
		arguments = ["python", "-u", "destroyer.py"   , txt, name, "1"]

	prefix = f"P-{UFID(ID, 3)}"

	if arguments is not None:
		prettyRun(prefix, arguments)
	
	tt = '@'+reply._json['user']['screen_name']
	tt = "" if tt.lower() == '@videoeditbot' else tt

	now = datetime.datetime.now()
	millis = str(int(round(time.time() * 1000)))

	folder = DIRECTORY
	foldName = reply._json['user']['screen_name']
	newFolder = f"{folder}/{foldName}"
	finalName = f"{uniquePrefix}_{ID}.{mediaType}"
	fileName = f"_{foldName}_{millis}_{now.year}-{now.month}-{now.day}-{now.hour}.{now.minute}.{now.second}_{finalName[-6:]}"
	newLocation = f"{newFolder}/{fileName}"
	newURL = f"files.ganer.xyz/Twitter/{fileName}"

	cannotPost = False

	def bpnt(m):
		print(f"{prefix}:\t\t{m}")

	#Codes:
	# -1: could not tweet text based reply
	# 0 : told the user that there was an error
	# 1 : send text based reply with link, but reasoning was not handled (ex. duration, aspect ratio, etc.)
	# 2 : sucessfully uploaded video to twitter

	def backup():
		if os.path.isdir(newFolder) is not True:
			os.makedirs(newFolder)
		os.rename(finalName, newLocation)
	#Check if video exists
	try:
		backup()
	except Exception as e:
		try:
			api.update_status(f"{tt} Something went wrong processing your edit, inform Ganer if this is a mistake.", in_reply_to_status_id = str(reply.id), auto_populate_reply_metadata=True)
			bpnt("Tweet posted (0) (Backup failed)")
			return
		except tweepy.TweepError as b:
			bpnt("WARN (-1) (Backup failed) "+str(b.api_code))
			return
	#Try and upload the video
	try:
		fsize = os.path.getsize(newLocation) / (1024 ** 2)
		if fsize > 15.5:
			api.update_status(f"Your video was too large to directly upload, here is a backup of the result: {newURL}", in_reply_to_status_id = str(reply.id), auto_populate_reply_metadata=True)
			bpnt("Tweet posted (1.5)")
		else:
			mediaID = api.media_upload(newLocation)
			time.sleep(5)
			api.update_status('', media_ids=[mediaID.media_id_string], in_reply_to_status_id = str(reply.id), auto_populate_reply_metadata=True)
			bpnt("Tweet posted (2)")
			return
	except Exception as e: #If it failed
		try:
			bpnt(e.message[0]['code'])
			api.update_status(f"Something went wrong uploading your video, here is a backup of the result: {newURL}", in_reply_to_status_id = str(reply.id), auto_populate_reply_metadata=True)
			bpnt("Tweet posted (1)")
			return
		except Exception as b:
			try:
				api.update_status(f"{tt} Something went wrong processing your edit, if you think this is a mistake please inform Ganer.", in_reply_to_status_id = str(reply.id), auto_populate_reply_metadata=True)
				bpnt("Tweet posted (0)")
				return
			except Exception as e3:
				bpnt("WARN (-1) "+str(e3.api_code))
				return

def callBot(e, ID, mostRecentTweet, uniquePrefix, reply, isRetweet = False):
	global count
	if 'media' in e:
		m = e['media'][0]
		try:
			folder = DIRECTORY
			foldName = reply._json['user']['screen_name']
			if os.path.isdir(f"{folder}/{foldName}") is not True:
				os.makedirs(f"{folder}/{foldName}")
			thread = threading.Thread(target=getContent, args = [m, ID, mostRecentTweet, uniquePrefix, reply, isRetweet])
			thread.start()
			count += 1
		except Exception as e:
			print("Error!", e)
	else:
		pass

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
		print("Error:", e)
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
			topUser = api.get_status(mostRecentTweet._json['in_reply_to_status_id_str'], tweet_mode = 'extended')
			topUserE = topUser._json['entities']
			#print(mostRecentTweet)
			topTweetTagCount = (topUser._json['full_text'].lower()+'@'+topUser._json['user']['screen_name']).count("@videoeditbot")
			tagCount = mostRecentTweet._json['full_text'].lower().count("@videoeditbot")
			isReplyToMyTweet = (not topUser._json['in_reply_to_status_id_str']) and topUser._json['user']['screen_name'] == "@videoeditbot"
			if topTweetTagCount > 0 and not isReplyToMyTweet:
				if tagCount < 2:
					continue
			if tagCount > 0 or isReplyToMyTweet:
				callBot(topUserE, topUser._json['id'], topUser, uniquePrefix, mostRecentTweet)
			# if "@videoeditbot" in (topUser._json['full_text']+'@'+topUser._json['user']['screen_name']).lower():
			# 	if mostRecentTweet._json['full_text'].lower().count("@videoeditbot") < 2:
			# 		#print("Tweet is reply without extra mention, ignoring.")
			# 		continue
			
		else:
			try:
				topUser = api.get_status(mostRecentTweet._json['quoted_status_id_str'], tweet_mode = 'extended')
				topUserE = topUser._json['entities']
				callBot(topUserE, topUser._json['id'], topUser	, uniquePrefix, mostRecentTweet, isRetweet = True)
			except Exception as e:
				continue
	if count > 0:
		print(f"Executed destroyer for {count} tweet{'s' if count > 1 else ''}.")
