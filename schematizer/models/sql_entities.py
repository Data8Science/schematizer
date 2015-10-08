# -*- coding: utf-8 -*-
"""
This module contains the internal data structure to hold the information
of parsed SQL schemas.
"""
from itertools import izip


class SQLTable(object):
    """Internal data structure that represents a general sql table.
    """

    def __init__(self, table_name, columns=None, doc=None, **metadata):
        self.name = table_name
        self.columns = columns or []
        self.doc = doc
        # any additional metadata that does not belong to sql table
        # definition but would like to be tracked.
        self.metadata = metadata

    def __eq__(self, other):
        return (isinstance(other, SQLTable) and
                self.name == other.name and
                self.columns == other.columns and
                self.metadata == other.metadata)

    def test(self):
        assert False

    def assert_equal(self, other):
        assert isinstance(other, SQLTable)
        assert self.name == other.name
        for my_column, other_column in izip(self.columns, other.columns):
            my_column.assert_equal(other_column)
        assert self.metadata == other.metadata

    @property
    def primary_keys(self):
        return sorted(
            (col for col in self.columns if col.primary_key_order),
            key=lambda c: c.primary_key_order
        )


class SQLColumn(object):
    """Internal data structure that represents a general sql column.
    It is intended to support sql column definition in general. The
    column type could be database specific.
    """

    def __init__(self, column_name, column_type, primary_key_order=None,
                 is_nullable=True, default_value=None,
                 attributes=None, doc=None, **metadata):
        self.name = column_name
        self.type = column_type
        self.primary_key_order = primary_key_order
        self.is_nullable = is_nullable
        self.default_value = default_value
        self.doc = doc
        # attributes contain column settings except default value and nullable
        self.attributes = set(attributes or [])
        self._attributes_lookup = dict((attr.name, attr)
                                       for attr in self.attributes)
        # any additional metadata that does not belong to sql column
        # definition but would like to be tracked, such as alias
        self.metadata = metadata

    def get_attribute(self, key):
        return self._attributes_lookup.get(key)

    def __eq__(self, other):
        return (isinstance(other, SQLColumn) and
                self.name == other.name and
                self.type == other.type and
                self.primary_key_order == other.primary_key_order and
                self.is_nullable == other.is_nullable and
                self.default_value == other.default_value and
                self.attributes == other.attributes and
                self.metadata == other.metadata)

    def assert_equal(self, other):
        assert isinstance(other, SQLColumn)
        assert self.name == other.name
        assert self.type == other.type
        assert self.primary_key_order == other.primary_key_order
        assert self.is_nullable == other.is_nullable
        assert self.default_value == other.default_value
        for my_attribute, other_attribute in izip(
            self.attributes,
            other.attributes
        ):
            my_attribute.assert_equal(other_attribute)
        assert self.metadata == other.metadata


class SQLAttribute(object):
    """Class that holds the sql attributes in the table/column definitions,
    such as column default value, nullable property, character set, etc.
    """

    def __init__(self, name):
        self.name = name
        self.value = None
        self.has_value = False

    @classmethod
    def create_with_value(cls, name, value):
        attribute = SQLAttribute(name)
        attribute.name = name
        attribute.value = value
        attribute.has_value = True
        return attribute

    def __eq__(self, other):
        return (isinstance(other, SQLAttribute) and
                self.name == other.name and
                self.value == other.value and
                self.has_value == other.has_value)

    def __hash__(self):
        return hash((self.name, self.value, self.has_value))

    def assert_equal(self, other):
        assert isinstance(other, SQLAttribute)
        assert self.name == other.name
        assert self.value == other.value
        assert self.has_value == other.has_value


class SQLColumnDataType(object):
    """Internal data structure that contains column data type information.
    """

    type_name = None

    def __init__(self, attributes=None):
        self.attributes = set(attributes or [])
        self._attributes_lookup = dict((attr.name, attr)
                                       for attr in self.attributes)

    def attribute_exists(self, name):
        return name in self._attributes_lookup

    def get_attribute(self, name):
        return self._attributes_lookup.get(name)

    def __eq__(self, other):
        return (isinstance(other, SQLColumnDataType) and
                self.attributes == other.attributes)

    def to_value(self, val_string):
        """Convert the given string representation of the value to the value
        of this data type.  Each data type is responsible for converting the
        string to the value of correct type.  It returns `None` if the given
        string is missing or `null`.  Otherwise, it returns the original value
        string by default.
        """
        if self._is_null_string(val_string):
            return None
        else:
            return self._string_to_value(val_string)

    def _string_to_value(self, val_string):
        """Convert the given string representation of the value to the value
        of this data type.  Each data type is responsible for converting the
        string to the value of correct type.
        """
        raise NotImplementedError('Must be implemented by subclasses')

    def _is_null_string(self, val_string):
        return val_string is None or val_string.lower() == 'null'


class MetaDataKey(object):
    """Key of metadata attributes"""

    NAMESPACE = 'namespace'
    ALIASES = 'aliases'
    PERMISSION = 'permission'


class DbPermission(object):

    def __init__(
        self,
        object_name,
        user_or_group_name,
        permission,
        for_group=False
    ):
        self.object_name = object_name
        self.user_or_group_name = user_or_group_name
        self.permission = permission
        self.for_group = for_group

    def __eq__(self, other):
        return (isinstance(other, DbPermission) and
                self.object_name == other.object_name and
                self.user_or_group_name == other.user_or_group_name and
                self.permission == other.permission and
                self.for_group == other.for_group)
