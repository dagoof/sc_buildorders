import functools, operator, datetime, bcrypt
import decorators, sc_units, sc_orders
from build_orders import db

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

"""
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
    created = db.DateTime()
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
"""
