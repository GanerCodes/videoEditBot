@ECHO OFF
TITLE Discord
:loop
python socketWrap.py "python -u discordBot.py" 2
goto loop