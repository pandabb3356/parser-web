import datetime
import json
import re

import sqlalchemy
from sqlalchemy.ext.mutable import Mutable

from web.constants import DATETIME_FORMAT


class Enum(sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.SmallInteger

    def __init__(self, enum_class, **kwargs):
        super().__init__(**kwargs)
        self._enum_class = enum_class

    def process_bind_param(self, value, dialect):
        return value.value

    def process_result_value(self, value, dialect):
        return self._enum_class(value)

    @property
    def python_type(self):
        return self._enum_class


def _default_handler(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime(DATETIME_FORMAT)

    raise TypeError(repr(obj) + " is not JSON serializable")


DATETIME_RE = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', (re.VERBOSE | re.MULTILINE | re.DOTALL))


def _object_hook(obj):
    for key in obj:
        value = obj[key]
        if isinstance(value, str) and DATETIME_RE.match(value):
            obj[key] = datetime.datetime.strptime(value, DATETIME_FORMAT)
    return obj


class JsonEncoded(sqlalchemy.types.TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""

    impl = sqlalchemy.types.String

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value, default=_default_handler)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value, object_hook=_object_hook, strict=False)
        return value

    def compare_values(self, first, second):
        return False


class MutationDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutationDict):
            if isinstance(value, dict):
                return MutationDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.changed()

    def __getstate__(self):
        return dict(self)


class MutationList(Mutable, list):
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutationList):
            if isinstance(value, list):
                return MutationList(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, idx, value):
        list.__setitem__(self, idx, value)
        self.changed()

    def __setslice__(self, start, stop, values):
        list.__setslice__(self, start, stop, values)
        self.changed()

    def __delitem__(self, idx):
        list.__delitem__(self, idx)
        self.changed()

    def __delslice__(self, start, stop):
        list.__delslice__(self, start, stop)
        self.changed()

    def append(self, value):
        list.append(self, value)
        self.changed()

    def insert(self, idx, value):
        list.insert(self, idx, value)
        self.changed()

    def extend(self, values):
        list.extend(self, values)
        self.changed()

    def pop(self, *args, **kw):
        value = list.pop(self, *args, **kw)
        self.changed()
        return value

    def remove(self, value):
        list.remove(self, value)
        self.changed()

    def __getstate__(self):
        return list(self)

    def __setstate__(self, state):
        pass


def JsonObject(sqltype):
    class _JsonEncoded(JsonEncoded):
        impl = sqltype

    return MutationDict.as_mutable(_JsonEncoded)


def JsonArray(sqltype):
    class _JsonEncoded(JsonEncoded):
        impl = sqltype

    return MutationList.as_mutable(_JsonEncoded)
