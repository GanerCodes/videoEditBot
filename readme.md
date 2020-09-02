# Edits videos through Twitter and Discord.

Requires:
 - Python 3.8 (Libs = ffmpeg, pydub, discord, tweepy, pillow, colorama, requests, youtube_dl, aiohttp, asyncio)
 - Ruby 2.7 (Libs = aviglitch)
 - Ffmpeg
 - Sox

Create a file called "TOKENS.txt" and add sensitive info in this format:
```
discord = XXX

guilds = XXX, XXX, XXX...

consumer_key = XXX
consumer_secret = XXX
access_key = XXX
access_secret = XXX

log_ip = 0.0.0.0
```

There is also an optional "cookies.txt" file you can add that youtube-dl will use