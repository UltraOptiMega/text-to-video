import os

from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

import diskcache

from .constants import SECRET_KEY
from .views import index_bp
from .utils import render, init_tables


def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SECRET_KEY'] = SECRET_KEY

    CSRFProtect(app)
    Bootstrap5(app)

    app.register_blueprint(index_bp, url_prefix='/')

    cache = diskcache.Cache(f'{os.getcwd()}/.cache')
    app.cache = cache

    init_tables()

    @app.errorhandler(404)
    def page_not_found(error):
        return render('404.html'), 404

    @app.errorhandler(403)
    def page_forbidden(error):
        return render('403.html'), 403

    return app
