import collections

def is_iterable(o):
    return isinstance(o, collections.Sequence) and not isinstance(o, basestring)

def dict_create_path(path, into):
    this_section = into
    for index in path:
        if index not in this_section:
            this_section[index] = {}
        this_section = this_section[index]
    return this_section

def map_sub(f, _iter):
    _part = functools.partial(map_sub, f)
    if isinstance(_iter, collections.Mapping):
        k, v = zip(*_iter.items())
        return dict(zip(k, _part(v)))
    elif is_iterable(_iter):
        return map(_part, _iter)
    else:
        return f(_iter)
