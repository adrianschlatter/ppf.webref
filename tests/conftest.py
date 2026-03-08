import pytest
import shutil
from os import environ, mkdir, linesep
from tempfile import TemporaryDirectory
from pathlib import Path
from ppf.webref import create_app
from ppf.webref.model import db, User
from ppf.webref.passwords import hash_password


@pytest.fixture()
def app():
    with TemporaryDirectory() as tempdir:
        tempdir = Path(tempdir)
        environ['HOME'] = str(tempdir)
        mkdir(tempdir / Path('.config'))
        mkdir(tempdir / Path('.config/ppf.webref'))
        with open(
               tempdir / Path('.config/ppf.webref/ppf.webref.conf'), 'w') as f:
            f.write(linesep.join(['[flask]',
                                  'secret_key = dev',
                                  '[database]',
                                  'sqlusername = test',
                                  'sqlpassword = test',
                                  'sqlserver = test',
                                  'sqldatabasename = test']))

        app = create_app(test=True)
        references_dir = Path(app.root_path) / 'references'
        if references_dir.is_symlink():
            references_dir.unlink()
        elif references_dir.exists():
            shutil.rmtree(references_dir)

        user = User(username='existing_user',
                    pw_hash=hash_password('password'))
        with app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(user)
            db.session.commit()

        yield app

        if references_dir.is_symlink():
            references_dir.unlink()
        elif references_dir.exists():
            shutil.rmtree(references_dir)

        with app.app_context():
            db.session.remove()
            db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
