import pytest
from pathlib import Path
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
    entry_missing_file = Entry(type='article', version=1,
                               fields={
                                   'author': 'Missing File',
                                   'title': 'Feedback Missing File',
                                   'year': '2021',
                                   'file': ':missing.pdf:PDF'})
    entry_absolute_file = Entry(type='article', version=1,
                                fields={
                                    'author': 'Absolute File',
                                    'title': 'Feedback Absolute File',
                                    'year': '2022',
                                    'file': ':/tmp/abs.pdf:PDF'})
    entry_no_file = Entry(type='article', version=1,
                          fields={
                              'author': 'No File',
                              'title': 'Feedback Without File',
                              'year': '2023'})

    with app.app_context():
        db.session.add_all([
            entry,
            entry_missing_file,
            entry_absolute_file,
            entry_no_file,
        ])
        db.session.commit()

    return client


def test_index(client_logged_in):
    response = client_logged_in.get('/', follow_redirects=True)
    assert b'ppf.webref' in response.data


def test_references_missing(client_logged_in):
    response = client_logged_in.get('/references/does_not_exist.pdf')
    assert response.status_code == 404


def test_references_existing(client_logged_in, app):
    with app.app_context():
        references_dir = Path(app.root_path) / 'references'
        references_dir.mkdir(exist_ok=True)
        reference_path = references_dir / 'a.pdf'
        reference_path.write_bytes(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')

    response = client_logged_in.get('/references/a.pdf')
    assert response.status_code == 200

    reference_path.unlink()


def test_loadEntries(client_logged_in, app):
    references_dir = Path(app.root_path) / 'references'
    references_dir.mkdir(exist_ok=True)
    reference_path = references_dir / 'a.pdf'
    reference_path.write_bytes(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')

    with client_logged_in as client:
        response = client.post('loadEntries.php',
                               data={'searchexpr': 'Feedback'})

    assert response.status_code == 200
    payload = response.get_json()
    entries = payload['entries']
    titles = [entry['title'] for entry in entries]
    assert payload['total_count'] == 4
    assert payload['returned_count'] == 4
    assert 'Feedback Systems' in titles
    assert 'Feedback Missing File' in titles
    assert 'Feedback Absolute File' in titles
    assert 'Feedback Without File' in titles
    file_entry = next(entry for entry in entries
                      if entry['title'] == 'Feedback Systems')
    assert file_entry['file'] == 'references/a.pdf'

    reference_path.unlink()


def test_loadEntries_sorting(client_logged_in):
    with client_logged_in as client:
        response = client.post('loadEntries.php',
                               data={'searchexpr': 'Feedback',
                                     'sort_by': 'year',
                                     'sort_dir': 'asc'})

    payload = response.get_json()
    years = [entry['year'] for entry in payload['entries']]
    assert years == ['2020', '2021', '2022', '2023']

    with client_logged_in as client:
        response = client.post('loadEntries.php',
                               data={'searchexpr': 'Feedback',
                                     'sort_by': 'year',
                                     'sort_dir': 'desc'})

    payload = response.get_json()
    years = [entry['year'] for entry in payload['entries']]
    assert years == ['2023', '2022', '2021', '2020']


def test_loadEntries_invalid_sort(client_logged_in):
    with client_logged_in as client:
        response = client.post('loadEntries.php',
                               data={'searchexpr': 'Feedback',
                                     'sort_by': 'publisher',
                                     'sort_dir': 'sideways'})

    payload = response.get_json()
    titles = [entry['title'] for entry in payload['entries']]
    assert payload['total_count'] == 4
    assert payload['returned_count'] == 4
    assert 'Feedback Systems' in titles


def test_get_entry_details(client_logged_in, app):
    references_dir = Path(app.root_path) / 'references'
    references_dir.mkdir(exist_ok=True)
    reference_path = references_dir / 'a.pdf'
    reference_path.write_bytes(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')

    with app.app_context():
        entry = (db.session.execute(
            db.select(Entry).order_by(Entry.shared_id)
        ).scalars().first())

    response = client_logged_in.get(
        f'/getEntry?shared_id={entry.shared_id}'
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['title'] == 'Feedback Systems'
    assert payload['authors'] == 'Åström, Karl Johan and Murray, Richard M.'
    assert payload['date'] == '2020'
    assert payload['type'] == 'article'
    assert payload['citationkey'] == 'a'
    assert payload['files'] == [{'label': 'a.pdf', 'href': 'references/a.pdf'}]

    reference_path.unlink()


def test_get_entry_missing_id(client_logged_in):
    response = client_logged_in.get('/getEntry')
    assert response.status_code == 400


def test_get_entry_not_found(client_logged_in):
    response = client_logged_in.get('/getEntry?shared_id=999999')
    assert response.status_code == 404


def test_loadEntries_field_query(client_logged_in):
    with client_logged_in as client:
        response = client.post('loadEntries.php',
                               data={'searchexpr': 'author:Åström'})

    payload = response.get_json()
    titles = [entry['title'] for entry in payload['entries']]
    assert payload['total_count'] == 1
    assert payload['returned_count'] == 1
    assert 'Feedback Systems' in titles
    assert 'Feedback Missing File' not in titles


def test_loadEntries_logical_query(client_logged_in):
    with client_logged_in as client:
        response = client.post(
            'loadEntries.php',
            data={'searchexpr': 'title:"Feedback Systems" AND year:2020'})

    payload = response.get_json()
    titles = [entry['title'] for entry in payload['entries']]
    assert payload['total_count'] == 1
    assert payload['returned_count'] == 1
    assert 'Feedback Systems' in titles
    assert 'Feedback Missing File' not in titles


def test_loadEntries_invalid_field(client_logged_in):
    with client_logged_in as client:
        response = client.post('loadEntries.php',
                               data={'searchexpr': 'editor:Smith'})

    payload = response.get_json()
    assert payload['total_count'] == 0
    assert payload['returned_count'] == 0
    assert payload['entries'] == []
