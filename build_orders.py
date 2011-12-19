import functools, collections, jinja2
from flask import Flask, request, redirect, url_for, render_template, g,\
        session, abort, jsonify, flash
from flaskext.sqlalchemy import SQLAlchemy
from sc_units import all_gameunits
from sc_orders import BuildOrder

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

SECRET_KEY = 'devkey'
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///build_orders.db'
db = SQLAlchemy(app)

class Build(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    
    def __init__(self):
        pass

    @property
    def units(self):
        return map(operator.methodgetter('unit'), self.elements)

    @property
    def order(self):
        return BuildOrder(*self.units)

    def __repr__(self):
        return '<Build %r>' % self.id

class Element(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    build_id = db.Column(db.Integer, db.ForeignKey('build.id'),
            nullable = False)
    build = db.relationship(Build, backref = db.backref('elements'))
    index = db.Column(db.Integer, nullable = False)
    unit_name = db.Column(db.String, nullable = False)

    def __init__(self, build, index, unit_name):
        self.build = build
        self.index = index
        self.unit_name = unit_name

    @property
    def unit(self):
        return all_gameunits[unit_name]

    def __repr__(self):
        return '<Element %r>' % self.unit



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
