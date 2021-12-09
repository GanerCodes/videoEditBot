import traceback, asyncio, time
from uuid import uuid4
from threading import Thread
from collections import namedtuple

action_result = namedtuple("action_result", "success value")
swap_arg = namedtuple("swap_arg", "name")
async_handler_action = namedtuple("async_handler_action", "func args kwargs")

class Async_handler:
    def __init__(self, timeout = 300, refresh_rate = 1, action_refresh_rate = 1):
        self.que = {}
        self.timeout = timeout
        self.refresh_rate = refresh_rate
        self.action_refresh_rate = action_refresh_rate

    def run(self, func, *args, **kwargs):
        ide = str(uuid4())
        self.que[ide] = (param := async_handler_action(func, args, kwargs))
        for i in range(self.timeout):
            if self.que[ide] == param:
                time.sleep(self.action_refresh_rate)
            else:
                ret = self.que[ide]
                del self.que[ide]
                return ret
        else:
            del self.que[ide]
            return Exception("Timeout")
    
    async def looper(self):
        while True:
            for ide, action in self.que.items():
                if type(action) == async_handler_action:
                    try:
                        self.que[ide] = (await action.func(*action.args, **action.kwargs))
                    except Exception as err:
                        self.que[ide] = err
                         
            await asyncio.sleep(self.refresh_rate)

class Action:
    def __init__(self, func, *args, fails_task = True, name = "Action", check = None, parse = None, fail_action = None, success_action = None, **kwargs):
        self.func           = func
        self.args           = list(args)
        self.kwargs         = kwargs
        self.name           = name
        self.parse          = parse or (lambda x: {"result": x})
        self.check          = check or (lambda x: True)
        self.fails_task     = fails_task
        self.fail_action    = fail_action
        self.success_action = success_action
        self.async_handler  = None
    
    def execute(self, *args, **kwargs):
        args   = args   or self.args  .copy()
        kwargs = kwargs or self.kwargs.copy()
        try:
            if asyncio.iscoroutinefunction(self.func):
                if self.async_handler:
                    value = self.async_handler.run(self.func, *args, **kwargs)
                    if type(value) == Exception:
                        raise value
                else:
                    return action_result(False, "Unable to run async function: no async handler specified.")
            else:
                value = self.func(*args, **kwargs)
            result = self.parse(value)
            
            if self.check(result):
                return action_result(True, result)
            else:
                return action_result(False, result)
        except Exception as err:
            return action_result(False, err)
    
    def __str__(self):
        return f'''func="{self.func.__name__}" args="{self.args}" fails_task="{self.fails_task}" kwargs="{self.kwargs}"'''

class Task:
    def __init__(self, *actions, fail_handler = None, success_handler = None, async_handler = None, persist_result_values = False):
        self.fail_handler = fail_handler or (
            lambda name, err: print(f"{name}: Error!", ''.join(traceback.format_exception(err)), self)
        )
        self.success_handler = success_handler or (lambda name, val: ())
        self.async_handler = async_handler
        self.persist_result_values = persist_result_values
        
        self.actions = list(actions)
        if len(self.actions):
            self.actions[0].first = True
        for action in self.actions:
            action.async_handler = self.async_handler

    def run(self):
        result = {}
        for action_index, action in enumerate(self.actions):
            args = [(
                result[v.name] if type(v) == swap_arg else v
            ) for v in action.args]
            
            kwargs = {k: (
                result[v.name] if type(v) == swap_arg else v
            ) for k, v in action.kwargs.items()}
            
            cur_result = action.execute(*args, **kwargs) # success, value
            if not cur_result.success: # Failed
                if action.fail_action: # Run action's built in fail handler
                    action.fail_action.execute(action.name, cur_result.value)
                if action.fails_task: # Run task failed action
                    return self.fail_handler(action.name, cur_result.value)
            else: # Success
                if action.success_action: # Run action's built in success handler
                    action.success_action.execute(action.name, cur_result.value)
                self.success_handler(action.name, cur_result.value) # Run task success action
            
            if self.persist_result_values:
                result |= cur_result.value # Merge previous results
            else:
                result = cur_result.value # Overwrite previous results
        return result["result"] if "result" in result else result
    
    def run_threaded(self):
        Thread(target = self.run).start()

if __name__ == '__main__':
    def f1(a, b):
        return f"{a} {b}"

    def f2(k, cheese = None):
        return k * 2 + cheese

    def f3(k):
        return f"sus {k}"

    print(Task(
        Action(f1, 2, 2, name = "#1",
            parse = lambda x: {"a": x, "b": " haha"}),
        Action(f2, swap_arg("a"), cheese = swap_arg("b"),
            name = "#2"),
        Action(f3, swap_arg("result"),
            name = "#3"),
        success_handler = lambda name, val: print(f'{name} says "{val}"')
    ).run())