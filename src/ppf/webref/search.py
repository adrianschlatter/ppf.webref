from dataclasses import dataclass
from typing import Optional

from sqlalchemy import exists, false

from ppf.webref.model import db, Entry, Field


ALLOWED_FIELDS = {
    'author',
    'title',
    'publisher',
    'year',
    'citationkey',
    'keywords',
    'month',
    'url',
    'file',
}


@dataclass(frozen=True)
class Token:
    kind: str
    value: Optional[str] = None


@dataclass(frozen=True)
class Term:
    field: Optional[str]
    value: str


@dataclass(frozen=True)
class Unary:
    op: str
    expr: object


@dataclass(frozen=True)
class Binary:
    op: str
    left: object
    right: object


def _term_condition(term):
    pattern = f"%{term.value}%"
    if term.field:
        return exists(
            db.select(Field.entry_shared_id)
            .where(Field.entry_shared_id == Entry.shared_id,
                   Field.name == term.field,
                   Field.value.ilike(pattern))
        )
    return exists(
        db.select(Field.entry_shared_id)
        .where(Field.entry_shared_id == Entry.shared_id,
               Field.name.in_(ALLOWED_FIELDS),
               Field.value.ilike(pattern))
    )


def tokenize(expression):
    tokens = []
    i = 0
    length = len(expression)
    while i < length:
        char = expression[i]
        if char.isspace():
            i += 1
            continue
        if char == '(':
            tokens.append(Token('LPAREN'))
            i += 1
            continue
        if char == ')':
            tokens.append(Token('RPAREN'))
            i += 1
            continue
        if char == ':':
            tokens.append(Token('COLON'))
            i += 1
            continue
        if char == '"':
            i += 1
            start = i
            value = []
            while i < length:
                char = expression[i]
                if char == '\\' and i + 1 < length:
                    value.append(expression[i + 1])
                    i += 2
                    continue
                if char == '"':
                    break
                value.append(char)
                i += 1
            if i >= length or expression[i] != '"':
                raise ValueError('Unterminated string')
            tokens.append(Token('STRING', ''.join(value)))
            i += 1
            continue
        start = i
        while (i < length and not expression[i].isspace()
                and expression[i] not in '():'):
            i += 1
        word = expression[start:i]
        upper = word.upper()
        if upper in {'AND', 'OR', 'NOT'}:
            tokens.append(Token('OP', upper))
        else:
            tokens.append(Token('WORD', word))
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def current(self):
        if self.index >= len(self.tokens):
            return None
        return self.tokens[self.index]

    def consume(self):
        token = self.current()
        self.index += 1
        return token

    def accept(self, kind, value=None):
        token = self.current()
        if token is None:
            return None
        if token.kind != kind:
            return None
        if value is not None and token.value != value:
            return None
        self.index += 1
        return token

    def expect(self, kind, value=None):
        token = self.accept(kind, value=value)
        if token is None:
            raise ValueError('Unexpected token')
        return token

    def parse(self):
        expr = self.parse_or()
        if self.current() is not None:
            raise ValueError('Unexpected token')
        return expr

    def parse_or(self):
        expr = self.parse_and()
        while self.accept('OP', 'OR'):
            right = self.parse_and()
            expr = Binary('OR', expr, right)
        return expr

    def parse_and(self):
        expr = self.parse_not()
        while self.accept('OP', 'AND'):
            right = self.parse_not()
            expr = Binary('AND', expr, right)
        return expr

    def parse_not(self):
        if self.accept('OP', 'NOT'):
            return Unary('NOT', self.parse_not())
        return self.parse_primary()

    def parse_primary(self):
        if self.accept('LPAREN'):
            expr = self.parse_or()
            self.expect('RPAREN')
            return expr
        return self.parse_term()

    def parse_term(self):
        token = self.current()
        if token is None:
            raise ValueError('Unexpected end of input')
        if token.kind == 'WORD':
            if ((self.index + 1) < len(self.tokens)
                    and self.tokens[self.index + 1].kind == 'COLON'):
                field = token.value.lower()
                if field not in ALLOWED_FIELDS:
                    raise ValueError('Unknown field')
                self.consume()
                self.consume()
                value = self.parse_value()
                return Term(field, value)
        value = self.parse_value()
        return Term(None, value)

    def parse_value(self):
        token = self.current()
        if token is None:
            raise ValueError('Unexpected end of input')
        if token.kind == 'STRING':
            self.consume()
            return token.value
        if token.kind == 'WORD':
            self.consume()
            return token.value
        raise ValueError('Unexpected token')


def _build_condition(expr):
    if isinstance(expr, Term):
        return _term_condition(expr)
    if isinstance(expr, Unary) and expr.op == 'NOT':
        return ~_build_condition(expr.expr)
    if isinstance(expr, Binary):
        left = _build_condition(expr.left)
        right = _build_condition(expr.right)
        if expr.op == 'AND':
            return left & right
        if expr.op == 'OR':
            return left | right
    raise ValueError('Unsupported expression')


def build_entry_id_query(expression):
    if not expression or not expression.strip():
        return db.select(Entry.shared_id)
    tokens = tokenize(expression)
    parser = Parser(tokens)
    try:
        expr = parser.parse()
        condition = _build_condition(expr)
    except ValueError:
        return db.select(Entry.shared_id).where(false())
    return db.select(Entry.shared_id).where(condition)
