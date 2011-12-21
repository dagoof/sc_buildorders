import functools

def apply_f(applied_f):
    def decorator(f):
        @functools.wraps(f)
        def _wrapped(*args, **kwargs):
            return applied_f(f(*args, **kwargs))
        return _wrapped
    return decorator

def reverse_args(f):
    @functools.wraps(f)
    def _wrapped(*args):
        return f(*reversed(args))
    return _wrapped

def obj_to_kwargs(f):
    @functools.wraps(f)
    def _wrapped(obj):
        return f(**obj)
    return _wrapped

