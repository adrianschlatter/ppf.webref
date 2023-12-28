import pytest


@pytest.fixture()
def client_logged_in(app):
    client = app.test_client()
    client.post('login',
                data={'username': 'existing_user', 'password': 'password'})
    return client


def test_index(client_logged_in):
    response = client_logged_in.get('/', follow_redirects=True)
    assert b'ppf.webref' in response.data


def test_references(client_logged_in):
    response = client_logged_in.get('/references/does_not_exist.pdf')
    assert response.status_code == 404
