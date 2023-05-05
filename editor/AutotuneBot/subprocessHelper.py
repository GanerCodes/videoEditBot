from subprocess import DEVNULL, STDOUT, Popen, getoutput, check_output, check_call, PIPE, call, run as _run
from traceback import TracebackException

def printEx(e):
    print("".join(TracebackException.from_exception(e).format()))

def run(command, **kawrgs):
    return _run(command, **kawrgs)

def returnCode(command, **kawrgs):
    return call(command, **kawrgs)

def silent_run(command, **kawrgs):
    command = [str(i) for i in command]
    try:
        return check_call(command, stdout = DEVNULL, stderr = STDOUT, **kawrgs)
    except Exception as ex:
        print(f"Silent_run error:\n", command)
        printEx(ex)

def loud_run(command, **kawrgs):
    command = [str(i) for i in command]
    try:
        return check_call(command, **kawrgs)
    except Exception as ex:
        print(f"loud_run error:\n", command)
        printEx(ex)

def getout(command, **kawrgs):
    return _run(command, text = True, stdout = PIPE, **kawrgs).stdout.strip()

def getout_r(command, **kawrgs):
    r = _run(command, text = True, stdout = PIPE, **kawrgs)
    return [r.returncode, r.stdout]