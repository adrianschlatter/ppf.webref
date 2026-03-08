import pytest
from sqlalchemy.sql.selectable import Select

from ppf.webref.model import Entry, db
from ppf.webref.search import (
    build_entry_id_query,
    tokenize,
    Parser,
    Binary,
    Term,
    Token,
)


def _seed_entries(app):
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
    entry_missing = Entry(type='article', version=1,
                          fields={
                              'author': 'Missing File',
                              'title': 'Feedback Missing File',
                              'year': '2021',
                              'file': ':missing.pdf:PDF'})
    entry_other = Entry(type='article', version=1,
                        fields={
                            'author': 'Other Author',
                            'title': 'Other Title',
                            'year': '2022'})

    with app.app_context():
        db.session.add_all([entry, entry_missing, entry_other])
        db.session.commit()


def _entry_titles(app, entry_ids):
    with app.app_context():
        entries = db.session.execute(
            db.select(Entry).where(Entry.shared_id.in_(entry_ids))
        )
        return [entry[0].fields.get('title') for entry in entries]


def test_tokenize_basic():
    tokens = tokenize('author:Smith AND year:2020')
    kinds = [token.kind for token in tokens]
    values = [token.value for token in tokens]
    assert kinds == ['WORD', 'COLON', 'WORD', 'OP', 'WORD', 'COLON', 'WORD']
    assert values[0] == 'author'
    assert values[3] == 'AND'


def test_tokenize_string_escape():
    tokens = tokenize('title:"Machine \\\"Learning\\\""')
    assert tokens[0].kind == 'WORD'
    assert tokens[1].kind == 'COLON'
    assert tokens[2].kind == 'STRING'
    assert tokens[2].value == 'Machine "Learning"'


def test_tokenize_parentheses():
    tokens = tokenize('(author:Smith)')
    kinds = [token.kind for token in tokens]
    assert kinds == ['LPAREN', 'WORD', 'COLON', 'WORD', 'RPAREN']


def test_tokenize_unterminated_string_raises():
    with pytest.raises(ValueError):
        tokenize('title:"Machine')


def test_parse_or_and_not():
    tokens = tokenize('NOT (title:"Feedback Systems" OR year:2021)')
    parser = Parser(tokens)
    expr = parser.parse()
    assert expr.op == 'NOT'


def test_parse_unknown_field_rejected():
    tokens = tokenize('editor:Smith')
    parser = Parser(tokens)
    with pytest.raises(ValueError):
        parser.parse()


def test_parse_missing_rparen():
    tokens = tokenize('(author:Smith')
    parser = Parser(tokens)
    with pytest.raises(ValueError):
        parser.parse()


def test_parse_empty_tokens():
    parser = Parser([])
    with pytest.raises(ValueError):
        parser.parse()


def test_parse_value_unexpected_token():
    parser = Parser([Token('COLON')])
    with pytest.raises(ValueError):
        parser.parse_value()


def test_parse_value_unexpected_end():
    parser = Parser([])
    with pytest.raises(ValueError):
        parser.parse_value()


def test_accept_value_mismatch():
    parser = Parser([Token('OP', 'OR')])
    assert parser.accept('OP', 'AND') is None


def test_build_entry_id_query_empty_returns_all(app):
    _seed_entries(app)
    query = build_entry_id_query('')
    assert isinstance(query, Select)
    titles = _entry_titles(app, query)
    assert 'Feedback Systems' in titles
    assert 'Feedback Missing File' in titles
    assert 'Other Title' in titles


def test_build_entry_id_query_field_match(app):
    _seed_entries(app)
    query = build_entry_id_query('author:Åström')
    titles = _entry_titles(app, query)
    assert titles == ['Feedback Systems']


def test_build_entry_id_query_all_fields(app):
    _seed_entries(app)
    query = build_entry_id_query('Missing')
    titles = _entry_titles(app, query)
    assert titles == ['Feedback Missing File']


def test_build_entry_id_query_and_or_not(app):
    _seed_entries(app)
    query = build_entry_id_query(
        'author:Åström OR (title:"Feedback Missing File" AND NOT year:2022)'
    )
    titles = _entry_titles(app, query)
    assert 'Feedback Systems' in titles
    assert 'Feedback Missing File' in titles
    assert 'Other Title' not in titles


def test_build_entry_id_query_invalid_expression(app):
    _seed_entries(app)
    query = build_entry_id_query('author:')
    titles = _entry_titles(app, query)
    assert titles == []


def test_build_query_binary_invalid_op():
    term = Term('author', 'Smith')
    expr = Binary('XOR', term, term)
    with pytest.raises(ValueError):
        from ppf.webref.search import _build_condition

        _build_condition(expr)
