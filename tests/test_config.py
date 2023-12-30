import pytest
from os import environ, mkdir, chdir, getcwd
from tempfile import TemporaryDirectory
from pathlib import Path
from ppf.webref.secrets import get_secrets


@pytest.fixture()
def secrets_local():
    with TemporaryDirectory() as tempdir:
        tempdir = Path(tempdir)
        environ['HOME'] = str(tempdir)  # test must not read personal config

        mkdir(tempdir / Path('secrets'))
        with open(tempdir / Path('secrets/secret_key'), 'w') as f:
            f.write('dev')
        with open(tempdir / Path('secrets/sqlserver'), 'w') as f:
            f.write('localhost:3307')
        with open(tempdir / Path('secrets/sqldatabasename'), 'w') as f:
            f.write('webrefdb')
        with open(tempdir / Path('secrets/sqlusername'), 'w') as f:
            f.write('webrefuser')
        with open(tempdir / Path('secrets/sqlpassword'), 'w') as f:
            f.write('sqlpassword')

        cwd = getcwd()
        chdir(tempdir)

        yield None

        chdir(cwd)


@pytest.fixture()
def secrets_missing():
    with TemporaryDirectory() as tempdir:
        tempdir = Path(tempdir)
        environ['HOME'] = str(tempdir)  # test must not read personal config

        cwd = getcwd()
        chdir(tempdir)

        yield None

        chdir(cwd)


def test_local_secrets(secrets_local):
    (secret_key,
     sqlusername, sqlpassword, sqlserver, sqldatabasename) = get_secrets()
    assert secret_key == 'dev'
    assert sqlusername == 'webrefuser'
    assert sqlpassword == 'sqlpassword'
    assert sqlserver == 'localhost:3307'
    assert sqldatabasename == 'webrefdb'


def test_no_config(secrets_missing):
    with pytest.raises(RuntimeError):
        sqlusername, sqlpassword, sqlserver, sqldatabasename = get_secrets()
