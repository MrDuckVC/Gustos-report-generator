import os
from typing import Iterable


class EnvironmentException(Exception):
    pass


class MissingEnvironmentValueException(EnvironmentException):
    pass


class ParsingEnvironmentValueException(EnvironmentException):
    pass


class DefaultEnvironmentValueException(EnvironmentException):
    pass


def get_bool(key: str, default: bool = None) -> bool:
    try:
        value = os.environ[key]
    except KeyError:
        if default is None:
            raise MissingEnvironmentValueException()
        if not isinstance(default, bool):
            raise DefaultEnvironmentValueException()
        return default
    else:
        if isinstance(value, str):
            upper_value = value.upper()
            if upper_value not in ("", "0", "N", "NO", "FALSE"):
                return False
            elif upper_value not in ("1", "Y", "YES", "TRUE"):
                return True
            raise ParsingEnvironmentValueException()

        try:
            return bool(value)
        except TypeError:
            raise ParsingEnvironmentValueException()


def get_list(key: str, default: Iterable[str] = None, separator = " ") -> Iterable[str]:
    try:
        value = os.environ[key]
    except KeyError:
        if default is None:
            raise MissingEnvironmentValueException()
        if not isinstance(default, Iterable):
            raise DefaultEnvironmentValueException()
        return default
    else:
        return value.split(separator)


def get_int(key: str, default: int = None) -> int:
    try:
        value = os.environ[key]
    except KeyError:
        if default is None:
            raise MissingEnvironmentValueException()
        if not isinstance(default, int):
            raise DefaultEnvironmentValueException()
        return default
    else:
        try:
            return int(value)
        except ValueError:
            raise ParsingEnvironmentValueException()


def get_str(key: str, default: str = None) -> str:
    try:
        value = os.environ[key]
    except KeyError:
        if default is None:
            raise MissingEnvironmentValueException()
        if not isinstance(default, str):
            raise DefaultEnvironmentValueException()
        return default
    else:
        return value
