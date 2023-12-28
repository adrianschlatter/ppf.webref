import pytest
from os import environ, mkdir, linesep
from tempfile import TemporaryDirectory
from pathlib import Path
from ppf.webref import create_app
from ppf.webref.model import db, User


@pytest.fixture()
def app():
    with TemporaryDirectory() as tempdir:
        tempdir = Path(tempdir)
        environ['HOME'] = str(tempdir)
        mkdir(tempdir / Path('.config'))
        mkdir(tempdir / Path('.config/ppf.webref'))
        with open(
               tempdir / Path('.config/ppf.webref/ppf.webref.conf'), 'w') as f:
            f.write(linesep.join(['[database]',
                                  'sqlusername = test',
                                  'sqlpassword = test',
                                  'sqlserver = test',
                                  'sqldatabasename = test']))

        app = create_app(test=True)
        user = User(username='existing_user',
                    password=(b'$2b$12$jClUReA4eBjVLhTnNUf.QOHOKMg4IcFpRuu'
                              b'FHVYaLRXJ0msu0MG0K'))  # hashed 'password'
        with app.app_context():
            db.create_all()
            db.session.add(user)
            db.session.commit()

        yield app

        with app.app_context():
            db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
