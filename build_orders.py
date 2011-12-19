import functools, collections, jinja2, operator
from flask import Flask, request, redirect, url_for, render_template, g,\
        session, abort, jsonify, flash
from flaskext.sqlalchemy import SQLAlchemy
from sc_units import all_gameunits
from sc_orders import BuildOrder, ZERG, zerg_base

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
        return map(operator.attrgetter('unit'), self.elements)

    @property
    def order(self):
        return ZERG(*self.units)

    @property
    def next_index(self):
        indexes = map(operator.attrgetter('index'), self.elements)
        return indexes and max(indexes) + 1 or 0

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
        return all_gameunits[self.unit_name]

    def __repr__(self):
        return '<Element %r>' % self.unit

def build_from_order(order):
    build = Build()
    for unit in order._unit_order:
        Element(build, build.next_index, str(unit))
    return build

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

@app.route('/build/<int:build_id>')
def build(build_id):
    build = Build.query.filter_by(id = build_id).first()
    return render_template('build.html', build = build)

@app.route('/build/create')
def build_create():
    build = build_from_order(zerg_base)
    db.session.add(build)
    db.session.add_all(build.elements)
    db.session.commit()
    return redirect(url_for('build', build_id = build.id))

@app.route('/build/add/<int:build_id>/<unit>')
def build_add(build_id, unit):
    build = Build.query.filter_by(id = build_id).first()
    element = Element(build, build.next_index, unit)
    db.session.add(element)
    try:
        db.session.commit()
    except Exception, e:
        db.session.rollback()
    return redirect(url_for('build', build_id = build_id))

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8096)
