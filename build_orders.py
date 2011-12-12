import functools, collections, jinja2
from flask import Flask, request, redirect, url_for, render_template, g,\
        session, abort, jsonify, flash
from sc_units import all_gameunits

def map_sub(f, _iter):
    _part = functools.partial(map_sub, f)
    if isinstance(_iter, collections.Mapping):
        k, v = zip(*_iter.items())
        return dict(zip(k, _part(v)))
    elif isinstance(_iter, collections.Sequence) and not\
            isinstance(_iter, basestring):
        return map(_part, _iter)
    else:
        return f(_iter)

def apply_f(applied_f):
    def decorator(f):
        @functools.wraps(f)
        def _wrapped(*args, **kwargs):
            return applied_f(f(*args, **kwargs))
        return _wrapped
    return decorator

def obj_to_kwargs(f):
    @functools.wraps(f)
    def _wrapped(obj):
        return f(**obj)
    return _wrapped

api_func = apply_f(obj_to_kwargs(jsonify))

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/external_render', methods = ['POST'])
def external_render():
    return jsonify(template = app.jinja_env.\
        from_string(request.json['template']).\
        render(**request.json['context']))

@app.route('/')
def index():
    return 'hello world'

def _unit_options(unit):
    return map_sub(str, all_gameunits[unit].data_obj)

@app.route('/api/unit_options/<unit>')
@api_func
def api_unit_options(*args, **kwargs):
    return _unit_options(*args, **kwargs)

@app.route('/unit_options/<unit>')
def unit_options(*args, **kwargs):
    return render_template('create.html',
            **_unit_options(*args, **kwargs))

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8096)
