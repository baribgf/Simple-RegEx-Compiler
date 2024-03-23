
debug = False

class ParseError(Exception):
    pass

def debuggable(fn):
    def wrap(*args, **kwargs):
        if debug:
            print(f"Invoking fn: '{fn.__name__}', with args: {args}")
            
        return fn(*args, **kwargs)
    
    return wrap

def set_debug_enabled(enable: bool=True):
    global debug
    debug = enable
