"""
app/models/base.py — SQLAlchemy declarative base.

All models import Base from here so Alembic's autogenerate can discover
every table by importing a single metadata object.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
