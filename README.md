# Edits videos through Twitter and Discord.

Requires:
 - Python 3.8+ (Libs = ffmpeg-python, pydub, discord, tweepy, pillow, colorama, requests, youtube_dl, aiohttp, asyncio)
 - Ruby 2.7+ (Libs = aviglitch)
 - Ffmpeg 4.3+
 - Sox 14.4+

Create a file called "TOKENS.txt" and add sensitive info in this format:
```
dir = XXX
website = XXX

discord = XXX
guilds = XXX, XXX, XXX...

consumer_key = XXX
consumer_secret = XXX
access_key = XXX
access_secret = XXX

log_ip = XXX
```

There is also an optional "cookies.txt" file you can add that youtube-dl will use
