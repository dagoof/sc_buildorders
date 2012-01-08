import functools, collections, jinja2, operator, decorators, func_utils
from flask import Flask, request, redirect, url_for, render_template, g,\
        session, abort, jsonify, flash
from flaskext.sqlalchemy import SQLAlchemy
from sc_units import all_gameunits
from sc_orders import race_orders, race_builds

api_func = decorators.apply_f(decorators.obj_to_kwargs(jsonify))

SECRET_KEY = 'devkey'
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trie_build_orders.db'
db = SQLAlchemy(app)

class Node(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    parent_id = db.Column(db.Integer, db.ForeignKey('node.id'),
            nullable = True)
    parent = db.relationship('Node', remote_side = [ id ])
    index = db.Column(db.Integer, nullable = False)
    unit_name = db.Column(db.String, nullable = False)

    def __init__(self, parent, index, unit_name):
        self.parent = parent
        self.index = index
        self.unit_name = unit_name

    @property
    def unit(self):
        return all_gameunits[self.unit_name]

    def __repr__(self):
        return '<Node %s %r>' % (self.index, self.unit)

class Build(db.Model):
    START_INDEX = 0
    id = db.Column(db.Integer, primary_key = True)
    race = db.Column(db.String, nullable = False)
    trie_id = db.Column(db.Integer, db.ForeignKey('node.id'),
            nullable = False)
    trie = db.relationship(Node, backref = db.backref('builds'))

    def __init__(self, race, trie):
        self.race = race
        self.trie = trie

    def add_unit(self, unit_name):
        for child in self.trie.children:
            if child.unit_name == unit_name and\
                    child.index == self.next_index:
                self.trie = child
                db.session.commit()
                return child
        self.trie = Node(self.trie, self.next_index, unit_name)
        db.session.add(self.trie)
        db.session.commit()
        return self.trie

    @staticmethod
    def from_order(race, order):
        if order:
            first_unit = next(iter(order._unit_order))
            first_node = Node.query.filter_by(parent = None,
                    unit_name = str(first_unit)).first()
            if first_node:
                build = Build(race, first_node)
            else:
                build = Build(race,
                        Node(None, Build.START_INDEX, str(first_unit)))
            for unit in order._unit_order[1:]:
                build.add_unit(str(unit))
            db.session.add(build)
            db.session.commit()

    @property
    def elements(self):
        return self.trie.full_ancestry

    @property
    def units(self):
        return map(operator.attrgetter('unit'), self.elements)

    @property
    def order(self):
        return race_orders[self.race](*self.units)

    @property
    def next_index(self):
        indexes = map(operator.attrgetter('index'), self.elements)
        return indexes and max(indexes) + 1 or Build.START_INDEX

    def __repr__(self):
        return '<%s Build %r>' % (self.race, self.id)

def build_from_order(race, order):
    build = Build(race)
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
    return func_utils.map_sub(str, all_gameunits[unit].data_obj)

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

@app.route('/build/create/<race>')
def build_create(race):
    build = Build.from_order(race, race_builds[race])
    return redirect(url_for('build', build_id = build.id))

@app.route('/build/add/<int:build_id>/<unit>')
def build_add(build_id, unit):
    build = Build.query.filter_by(id = build_id).first()
    build.add_unit(unit)
    return redirect(url_for('build', build_id = build_id))

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8096)
