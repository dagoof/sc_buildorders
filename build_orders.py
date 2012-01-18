import functools, operator, datetime
import flask, bcrypt
from flaskext.sqlalchemy import SQLAlchemy
import func_utils, decorators, sc_units, sc_orders

api_func = decorators.apply_f(decorators.obj_to_kwargs(flask.jsonify))

SECRET_KEY = 'devkey'
DEBUG = True
app = flask.Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trie_build_orders.db'
db = SQLAlchemy(app)

class Node(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    parent_id = db.Column(db.Integer, db.ForeignKey('node.id'),
            nullable = True)
    parent = db.relationship('Node', remote_side = [ id ],
            backref = 'children')
    index = db.Column(db.Integer, nullable = False)
    unit_name = db.Column(db.String, nullable = False)

    def __init__(self, parent, index, unit_name):
        self.parent = parent
        self.index = index
        self.unit_name = unit_name

    @property
    def unit(self):
        return sc_units.all_gameunits[self.unit_name]

    @property
    @decorators.apply_f(list)
    def full_ancestry(self):
        if self.parent:
            for more in self.parent.full_ancestry:
                yield more
        yield self

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
            first_unit = next(iter(order._unit_order), '')
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
            return build
        raise Exception('Cannot initialize a build based on an empty order')

    @property
    def elements(self):
        return self.trie.full_ancestry

    @property
    def units(self):
        return map(operator.attrgetter('unit'), self.elements)

    @property
    @decorators.apply_f(list)
    def distinguishing_features(self):
        for point in self.elements[8:]:
            if point.unit.allows:
                units = map(operator.attrgetter('unit'), point.parent.full_ancestry)
                order = sc_orders.race_orders[self.race](*units)
                yield point.unit, order.supply

    @property
    def order(self):
        return sc_orders.race_orders[self.race](*self.units)

    @property
    def next_index(self):
        indexes = map(operator.attrgetter('index'), self.elements)
        return indexes and max(indexes) + 1 or Build.START_INDEX

    def __repr__(self):
        return '<%s Build %r>' % (self.race, self.id)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique = True, nullable = False)
    email = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def create_password(self, password):
        return bcrypt.hashpw(password, bcrypt.gensalt())

    def set_password(self, password):
        self.password = self.create_password(password)
        return self.password

    def check_password(self, password):
        return bcrypt.hashpw(password, self.password) == self.password


class BuildDetails(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    build_id = db.Column(db.Integer, 
            db.ForeignKey('build.id'), nullable = False)
    build = db.relationship(Build, 
            backref = db.backref('details', uselist = False))
    user_id = db.Column(db.Integer, 
            db.ForeignKey('user.id'), nullable = False)
    user = db.relationship(User, 
            backref = 'build_details')
    created = db.DateTime(nullable = False)
    description = db.Column(db.String, nullable = False)

    def __init__(self, build, user, description):
        self.build = build
        self.user = user
        self.description = description
        self.created = datetime.datetime.now()


class Vote(db.Model):
    class Values:
        NO = 0
        YES = 1
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, 
            db.ForeignKey('user.id'), nullable = False)
    user = db.relationship(User, 
            backref = 'build_details')
    build_details_id = db.Column(db.Integer,
            db.ForeignKey('builddetails.id'), nullable = False)
    build_details = db.relationship(BuildDetails, backref = 'votes')
    value = db.Column(db.Integer, nullable = False)

    def __init__(self, user, build_details, value):
        self.user = user
        self.build_details = build_details
        self.value = value


@app.route('/external_render', methods = ['POST'])
def external_render():
    return flask.jsonify(template = app.jinja_env.\
        from_string(flask.request.json['template']).\
        render(**flask.request.json['context']))

@app.route('/')
def index():
    return 'hello world'

def _unit_options(unit):
    return func_utils.map_sub(str, sc_units.all_gameunits[unit].data_obj)

@app.route('/api/unit_options/<unit>')
@api_func
def api_unit_options(*args, **kwargs):
    return _unit_options(*args, **kwargs)

@app.route('/unit_options/<unit>')
def unit_options(*args, **kwargs):
    return flask.render_template('create.html',
            **_unit_options(*args, **kwargs))

@app.route('/build/<int:build_id>')
def build(build_id):
    build = Build.query.filter_by(id = build_id).first()
    return flask.render_template('build.html', build = build)

@app.route('/builds')
def builds():
    builds = Build.query.all()
    return flask.render_template('builds.html', builds = builds)

@app.route('/build/create/<race>')
def build_create(race):
    build = Build.from_order(race, sc_orders.race_builds[race])
    return flask.redirect(flask.url_for('build', build_id = build.id))

@app.route('/build/add/<int:build_id>/<unit>')
def build_add(build_id, unit):
    build = Build.query.filter_by(id = build_id).first()
    build.add_unit(unit)
    return flask.redirect(flask.url_for('build', build_id = build_id))

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8096)
