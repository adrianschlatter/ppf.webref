from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from flask_login import UserMixin


Base = declarative_base()


class User(Base, UserMixin):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(80), nullable=False)



db = SQLAlchemy()
