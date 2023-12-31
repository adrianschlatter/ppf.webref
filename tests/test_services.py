import pytest
from ppf.webref.model import Entry, db


@pytest.fixture()
def client_logged_in(app):
    client = app.test_client()
    client.post('login',
                data={'username': 'existing_user', 'password': 'password'})

    entry = Entry(type='article', version=1,
                  fields={
                      'author': 'Åström, Karl Johan and Murray, Richard M.',
                      'title': 'Feedback Systems',
                      'publisher': 'Princeton University Press',
                      'year': '2020',
                      'citationkey': 'a',
                      'month': '#jul#',
                      'url': ('http://www.cds.caltech.edu/~murray/books/AM08/'
                              'pdf/fbs-public_24Jul2020.pdf'),
                      'file': ':a.pdf:PDF',
                      'keywords': ('feedback, systems, continuous, control, '
                                   'stability, modeling, dynamics, '
                                   'linear systems, state space, t')})

    with app.app_context():
        db.session.add(entry)
        db.session.commit()

    return client


def test_index(client_logged_in):
    response = client_logged_in.get('/', follow_redirects=True)
    assert b'ppf.webref' in response.data


def test_references(client_logged_in):
    response = client_logged_in.get('/references/does_not_exist.pdf')
    assert response.status_code == 404


def test_loadEntries(client_logged_in):
    with client_logged_in as client:
        response = client.post('loadEntries.php',
                               data={'searchexpr': 'Feedback'})

    assert b'<table>' in response.data
    assert b'</table>' in response.data
    assert b'<td>Feedback Systems</td>' in response.data
