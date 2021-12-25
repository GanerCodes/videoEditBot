import traceback, asyncio, time
from uuid import uuid4
from threading import Thread
from collections import namedtuple

action_result = namedtuple("action_result", "success value")
swap_arg = namedtuple("swap_arg", "name")
async_handler_action = namedtuple("async_handler_action", "func args kwargs")

class Async_handler:
    def __init__(self, timeout = 300, refresh_rate = 1, action_refresh_rate = 1):
        self.que = {} # Que of functions to evaluate asynchronously 
        self.timeout = timeout # How long can a function be in que before timeout
        self.refresh_rate = refresh_rate # How many seconds between each check of function timeout
        self.action_refresh_rate = action_refresh_rate # How many seconds between executing the que 

    def run(self, func, *args, **kwargs):
        ide = str(uuid4()) # ID for function
        self.que[ide] = (param := async_handler_action(func, args, kwargs)) # Set up parameters
        for i in range(self.timeout):
            if self.que[ide] == param: # Unchanged value
                time.sleep(self.action_refresh_rate)
            else: # Value changed, return it
                ret = self.que[ide]
                del self.que[ide]
                return ret
        else: # Timed out
            del self.que[ide]
            return Exception("Timeout")
    
    async def looper(self):
        while True:
            try:
                for ide in list(self.que):
                    action = self.que[ide]
                    if type(action) == async_handler_action:
                        try: # Set que item to result
                            self.que[ide] = (await action.func(*action.args, **action.kwargs))
                        except Exception as err: # On failure, set result to error
                            self.que[ide] = err
            except Exception as err:
                print(f"Error in looper! {err}")
                        
            await asyncio.sleep(self.refresh_rate)

class Action:
    def __init__(self,
            func, *args,
            fails_task = True,
            name = "Action",
            check = None,
            parse = None,
            fail_action = None,
            success_action = None,
            skip_task_success_handler = False,
            skip_task_fail_handler = False,
            check_before_parse = True, 
            **kwargs):
        self.func = func # Function to run
        self.args = list(args) # Normal arguments for function
        self.kwargs = kwargs # keyword arguments for function
        self.name = name # Name for this action, mostly just used for logging purposes
        self.parse = parse or (lambda x: {"result": x}) # Function to apply on function result
        self.check = check or (lambda x: True) # Function to check if function result is successful
        self.check_before_parse = check_before_parse # Should we only parse before or after success checker
        self.fails_task = fails_task # Does action fail terminate tast?
        self.success_action = success_action # Action to perform on success
        self.fail_action = fail_action # Action to perform on failure
        self.skip_task_success_handler = skip_task_success_handler # On success, ignore task's general success handler
        self.skip_task_fail_handler = skip_task_fail_handler # On fail, ignore task's general fail handler
        self.async_handler = None # Handler to run async functions
    
    def execute(self, *args, **kwargs):
        args   = args   or self.args  .copy()
        kwargs = kwargs or self.kwargs.copy()
        try:
            if asyncio.iscoroutinefunction(self.func): # Execute async functions
                if self.async_handler:
                    value = self.async_handler.run(self.func, *args, **kwargs)
                    if type(value) == Exception:
                        raise value
                else:
                    return action_result(False, "Unable to run async function: no async handler specified.")
            else:
                value = self.func(*args, **kwargs) # Execute normal functions
            
            # Ordering and running of parse and check
            if self.check_before_parse:
                if checked_value := self.check(value):
                    result = self.parse(value)
                else:
                    result = value
            else:
                result = self.parse(result)
                checked_value = self.check(result)
            
            if checked_value:
                return action_result(True, result) # Return success
            else:
                return action_result(False, result) # Return failure
        except Exception as err:
            # return execution faliure 
            return action_result(False, err)
    
    def __str__(self):
        return f'''func="{self.func.__name__}" args="{self.args}" fails_task="{self.fails_task}" kwargs="{self.kwargs}"'''

class Task:
    def __init__(self,
            *actions,
            fail_handler = None,
            success_handler = None,
            async_handler = None,
            persist_result_values = False):
        self.actions = list(actions) # List of actions to perform
        self.success_handler = success_handler or (lambda name, val: ()) # Generic function to perform on action success 
        self.fail_handler = fail_handler or (
            lambda name, err: print(f"{name}: Error!", ''.join(traceback.format_exception(err)), self)
        ) # Generic function to perform on  action faliure 
        self.async_handler = async_handler # Handler to execute async functions
        self.persist_result_values = persist_result_values # Does the resulting value dictionary keep values from previous actions or only last action
        
        for action in self.actions: # Give actions the async handler
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
            if cur_result.success: # success
                if action.success_action: # Run action's built in success handler
                    action.success_action.execute(action.name, cur_result.value)
                if not action.skip_task_success_handler: # check task success override
                    self.success_handler(action.name, cur_result.value) # Run task success action
            else: # Failed
                if action.fail_action: # Run action's built in fail handler
                    action.fail_action.execute(action.name, cur_result.value)
                if action.fails_task: # Run task failed action
                    if action.skip_task_fail_handler: # check task fail override
                        return action.name, cur_result.value
                    else:
                        return self.fail_handler(action.name, cur_result.value)
            
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