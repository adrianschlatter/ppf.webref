# -*- coding: utf-8
"""
Web-Interface for JabRef library.

It lists the entries in a given JabRef library. It provides a simple
search bar to filter for those entries your looking for. Currently, it
provides read-only access to the library without any possibility to modify
existing entries or to add new ones.
"""

from flask import Flask, render_template, request, send_from_directory
from flask import url_for, redirect
from flask_login import login_user, LoginManager
from flask_login import login_required, logout_user
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from ppf.jabref import Entry, Field, split_by_unescaped_sep
from pathlib import Path
from .secrets import get_secrets
from .model import db, User
from .cli import reg_cli_cmds


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4)],
                             render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")


def create_app(test_config=None):
    # get secrets to access db:
    sqlusername, sqlpassword, sqlserver, sqldatabasename = get_secrets()
    # create and configure the app:
    app = Flask(__name__, static_url_path='', static_folder='static')
    # database configuration:
    app.config['SQLALCHEMY_DATABASE_URI'] = (
            f'mysql+pymysql://{sqlusername}:{sqlpassword}'
            f'@{sqlserver}/{sqldatabasename}')
    app.config['SECRET_KEY'] = '1YIYlxhBX6@el*ae'
    db.init_app(app)
    with app.app_context():
        db.create_all()
    # register command-line tools:
    reg_cli_cmds(app)

    # content security policy:
    csp = {'default-src': "'none'",
           'script-src':
           "'self' https://code.jquery.com https://cdnjs.cloudflare.com",
           'form-action': "'self'",
           'connect-src': "'self'",
           'style-src': "'self'",
           'base-uri': "'none'",
           'frame-ancestors': "'none'"}
    Talisman(app, content_security_policy=csp, force_https=False)
    bcrypt = Bcrypt(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    @login_required
    def root():
        """Show WebApp."""
        return render_template('index.php')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()

        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                if bcrypt.check_password_hash(
                        user.password, form.password.data):
                    login_user(user)
                    return redirect(url_for('root'))

        return render_template('login.php', form=form)

    @app.route('/logout', methods=['GET', 'POST'])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/references/<path:path>')
    @login_required
    def send_reference(path):
        """Send reference."""
        return send_from_directory('references', path)

    @app.route('/loadEntries.php', methods=['POST'])
    @login_required
    def loadEntries():
        """Return entries from library matching search expression."""
        searchexpr = request.form.get('searchexpr')

        patternmatchingQ = (db.select(Field.entry_shared_id)
                            .where(Field.value.op('rlike')(searchexpr))
                            .distinct())
        entryQ = (db.select(Entry)
                  .where(Entry.shared_id.in_(patternmatchingQ)))

        entries = [{f: entry[0].fields.get(f, None)
                   for f in ['author', 'title', 'year', 'file']}
                   for entry in db.session.execute(entryQ)]

        basepath = Path('references')
        for entry in entries:
            if entry['file'] is not None:
                filepath = Path(split_by_unescaped_sep(entry['file'])[1])
                entry['file'] = basepath / filepath
                if not entry['file'].exists() or filepath.is_absolute():
                    entry['file'] = None

        return render_template('entry_table.tmpl', entries=entries)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, use_debugger=False, use_reloader=False)
