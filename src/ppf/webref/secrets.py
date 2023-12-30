"""
Credential management

ppf.webref is meant to be run from the command line, often from inside a
docker container. Docker provides a mechanism to manage secrets. The user
creates a container, adds a (named) secret, and runs the container.
Inside the container, the named secret is available in the text file
/run/secrets/<secret-name>.

Outside of a docker container, having a config file in

~/.config/ppf.webref/ppf.webref.conf

is recommended.
"""

from plumbum import cli
from urllib.parse import quote_plus
from pathlib import Path


def get_secrets():
    config_path = Path('~/.config/ppf.webref/ppf.webref.conf').expanduser()
    if config_path.exists():
        with cli.Config(config_path) as config:
            secret_key = config.get('flask.secret_key', None)
            sqlusername = config.get('database.username', None)
            sqlpassword = config.get('database.password', None)
            sqlserver = config.get('database.server', None)
            sqldatabasename = config.get('database.databasename', None)
    else:
        secrets_path = Path('/run/secrets')
        if not secrets_path.exists():
            secrets_path = Path('./secrets')

        if secrets_path.exists():
            secret_key = open(secrets_path / 'secret_key').readline().strip()
            sqlusername = open(secrets_path / 'sqlusername').readline().strip()
            sqlpassword = open(secrets_path / 'sqlpassword').readline().strip()
            sqlserver = open(secrets_path / 'sqlserver').readline().strip()
            sqldatabasename = (open(secrets_path / 'sqldatabasename')
                               .readline().strip())
        else:
            raise RuntimeError('No config file found')

    sqlpassword = quote_plus(sqlpassword)
    return secret_key, sqlusername, sqlpassword, sqlserver, sqldatabasename
