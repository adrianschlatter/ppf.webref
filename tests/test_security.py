import pytest
from flask_login import current_user
import string
from ppf.webref.model import User


@pytest.fixture(params=['/', '/references/a.pdf', '/logout'])
def protected_endpoint(request):
    """Endpoints accessible only when logged in"""
    return request.param


@pytest.fixture(params=[string.printable, 'äéèüö'])
def password(request):
    """Passwords to test"""
    return request.param


def test_redirect_to_login(client, protected_endpoint):
    """No access when not logged in"""
    response = client.get(protected_endpoint)
    assert response.status_code == 302


def test_wrong_credentials(client, password):
    with client:
        client.post('login',
                    data={'username': 'test', 'password': password})
        assert current_user.is_authenticated is False


def test_correct_credentials(client):
    with client:
        client.post('login',
                    data={'username': 'existing_user', 'password': 'password'})
        assert current_user.is_authenticated is True
        client.get('logout')
        assert current_user.is_authenticated is False


def test_password_special_chars(client, app, runner, password, monkeypatch):
    with app.app_context():
        runner.invoke(args=['useradd', 'test'])
        monkeypatch.setattr('ppf.webref.cli.getpass', lambda: password)
        runner.invoke(args=['passwd', 'test'])

    with client:
        client.post('login', data={'username': 'test', 'password': password})
        assert current_user.is_authenticated is True


def test_useradd(app, runner):
    with app.app_context():
        result = runner.invoke(args=['useradd', 'test'])
        assert result.exit_code == 0
        assert User.query.filter_by(username='test').first() is not None


def test_useradd_existing(app, runner):
    with app.app_context():
        result = runner.invoke(args=['useradd', 'existing_user'])
        assert result.exit_code == 1
        assert User.query.filter_by(
                    username='existing_user').first() is not None


def test_userdel(app, runner):
    with app.app_context():
        result = runner.invoke(args=['userdel', 'existing_user'])
        assert result.exit_code == 0
        assert User.query.filter_by(username='existing_user').first() is None


def test_userdel_nonexisting(app, runner):
    with app.app_context():
        result = runner.invoke(args=['userdel', 'nonexisting user'])
        assert result.exit_code == 1
        assert User.query.filter_by(
                        username='nonexisting user').first() is None


def test_passwd_new(app, runner):
    with app.app_context():
        result = runner.invoke(args=['passwd', 'new user'])
        assert result.exit_code == 1


def test_passwd_existing(app, runner, monkeypatch):
    monkeypatch.setattr('ppf.webref.cli.getpass', lambda: 'password')
    with app.app_context():
        result = runner.invoke(args=['passwd', 'existing_user'])
        assert result.exit_code == 0
        user = User.query.filter_by(username='existing_user').first()
        assert user.password is not None
        assert user.password != 'password'  # password is hashed
