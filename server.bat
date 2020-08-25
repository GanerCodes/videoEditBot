@ECHO OFF
TITLE Files
:loop
python socketWrap.py "python -u server.py" 0
goto loop