@ECHO OFF
TITLE Twitter
:loop
python socketWrap.py "python -u twitterBot.py" 1
goto loop