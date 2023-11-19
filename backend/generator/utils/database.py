from typing import Sequence, Tuple

from django.conf import settings
from sqlalchemy import create_engine, Engine, Select
from sqlalchemy.sql.elements import KeyedColumnElement


def apply_range_filter(query: Select, column: Tuple[KeyedColumnElement, KeyedColumnElement] | KeyedColumnElement, value_range: Tuple[str | int, str | int]):
    if value_range is None:
        return query

    value_from, value_to = value_range
    if isinstance(column, Sequence):
        column_from, column_to = column
        if value_from is not None:
            query = query.where(column_from == value_from)
        if value_to is not None:
            query = query.where(column_to == value_to)
        return query
    else:
        if value_from is None:
            return query.where(column <= value_to)
        elif value_to is None:
            return query.where(column >= value_from)
        else:
            return query.where(column.between(value_from, value_to))


class Database:
    __instance: Engine = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = create_engine("mysql+mysqldb://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4".format(
                host=settings.DATABASES['gustos']['HOST'],
                port=settings.DATABASES['gustos']['PORT'],
                database=settings.DATABASES['gustos']['NAME'],
                user=settings.DATABASES['gustos']['USER'],
                password=settings.DATABASES['gustos']['PASSWORD'],
            ))
        return cls.__instance
