from functools import partial
import logging
import os.path
import random

from flask import Flask
from flask import request, url_for
from flask.json import jsonify
from mako.lookup import TemplateLookup

from snowflake.utils import LockBox

def slash(app):
    return render(app, 'slash')


def top_frame(app):
    authenticated = request.headers.get('Authenticated-User', None)
    cookied = request.cookies.get('user_name', '')

    default_name = authenticated or cookied or ''

    return render(app, 'top',
                  default_name=default_name)


def get_next(app):
    with app.config['db'] as db:
        found = db.get_next()
        labels = db.get_labels()

    return jsonify(
        url=found,
        labels=labels
    )


def rate(app):
    url = request.form['url']
    label = request.form['label']
    who = request.form['who']

    logging.info("%s rated %s as %s", who, url, label)

    with app.config['db'] as db:
        db.rate(url, who, label)

    return jsonify(
        success=True
    )


def render(app, name, **kw):
    kw.update(dict(
        app=app,
        url_for=url_for,
        static=lambda fname: url_for('static', filename=fname)))

    return app.config['mako'].get_template("%s.mako" % (name,)).render(**kw)


def make_app(db, debug=False):
    app = Flask(__name__)
    app.config['db'] = LockBox(db)
    app.config['debug'] = debug

    app.config['mako'] = TemplateLookup(
        directories=[os.path.join(os.path.dirname(__file__), 'templates')],
        cache_enabled=not app.config['debug'],
    )

    app.add_url_rule('/', 'slash', partial(slash, app))
    app.add_url_rule('/top', 'top', partial(top_frame, app))
    app.add_url_rule('/next', 'next', partial(get_next, app))
    app.add_url_rule('/rate', 'rate', partial(rate, app), methods=['POST'])

    return app
