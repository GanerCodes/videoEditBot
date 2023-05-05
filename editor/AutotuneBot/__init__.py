import os.path as path, sys, builtins
sys.path.insert(1, path.dirname(path.realpath(__file__)))
ex_defaults = {"_ctypes", "_collections_abc", "_compat_pickle", "_compression", "_ctypes", "_frozen_importlib", "_frozen_importlib_external"}
modi = {i: sys.modules.pop(i) for i in (set(sys.modules) - set(sys.builtin_module_names) - set(dir(builtins)) - ex_defaults)}

from autotune import autotuneURL, autotune

sys.path.pop()
for i in modi: sys.modules[i] = modi[i]