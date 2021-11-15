# Edits videos through Twitter and Discord.

Requires:
 - Python 3.8+ (Libs = ffmpeg-python, pydub, discord, tweepy, pillow, colorama, requests, yt-dlp, aiohttp, asyncio)
 - Ruby 2.7+ (Libs = aviglitch)
 - Ffmpeg 4.3+
 - Sox 14.4+

Create a file called "TOKENS.txt" and add sensitive info in this format:
```
dir = XXX
website = XXX
silent = XXX [true or false]

discord = XXX
guilds = XXX, XXX, XXX...

log_ip = XXX
host_ip = XXX
name = XXX
```

There is also an optional "cookies.txt" file you can add that youtube-dl will use
