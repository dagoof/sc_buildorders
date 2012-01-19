import functools, operator, datetime
import flask, bcrypt
import func_utils, decorators, sc_units, sc_orders
from build_orders import app
import models

api_func = decorators.apply_f(decorators.obj_to_kwargs(flask.jsonify))

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
    build = models.Build.query.filter_by(id = build_id).first()
    return flask.render_template('build.html', build = build)

@app.route('/builds')
def builds():
    builds = models.Build.query.all()
    return flask.render_template('builds.html', builds = builds)

@app.route('/build/create/<race>')
def build_create(race):
    build = models.Build.from_order(race, sc_orders.race_builds[race])
    return flask.redirect(flask.url_for('build', build_id = build.id))

@app.route('/build/add/<int:build_id>/<unit>')
def build_add(build_id, unit):
    build = models.Build.query.filter_by(id = build_id).first()
    build.add_unit(unit)
    return flask.redirect(flask.url_for('build', build_id = build_id))
