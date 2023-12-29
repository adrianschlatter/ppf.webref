from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy


db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=True)


# Everything below:
# Copy of ppf.jabref as we have to redefine the models based on db.Model:


class Entry(db.Model):
    """Represent a JabRef Entry."""

    __tablename__ = 'ENTRY'

    shared_id = db.Column('SHARED_ID', db.Integer, primary_key=True)
    type = db.Column(db.VARCHAR(255), nullable=False)
    version = db.Column(db.Integer, nullable=True)
    _fields = relationship(
        'Field',
        collection_class=attribute_mapped_collection('name'))

    # Access like entry.fields['author'] returns 'A. Muller'
    # which is nicer than using entry.fields['author'].value:
    fields = association_proxy('_fields', 'value',
                               creator=lambda k, v: Field(name=k, value=v))


class Field(db.Model):
    """Represent a JabRef Field."""

    __tablename__ = 'FIELD'

    entry_shared_id = db.Column(db.Integer, db.ForeignKey('ENTRY.SHARED_ID'),
                                primary_key=True)
    name = db.Column(db.VARCHAR(255), primary_key=True)
    value = db.Column(db.Text, nullable=True)
