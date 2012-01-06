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
