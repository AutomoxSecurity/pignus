"""A Dummy Model class to use for testing.

"""
from pignus.models.base import Base


FIELD_MAP = [
    {
        "name": "name",
        "type": "str",
        "extra": "UNIQUE"
    },
    {
        "name": "bool_field",
        "type": "bool",
        "extra": "NOT NULL"
    },
    {
        "name": "default_field",
        "type": "bool",
        "default": True
    },
    {
        "name": "int_field",
        "type": "int"
    },
    {
        "name": "list_field",
        "type": "list"
    },
    {
        "name": "date_field",
        "type": "datetime"
    },
]


class Dummy(Base):

    def __init__(self, conn=None, cursor=None):
        """Create the Dummy instance.
        :unit-test: test____init__
        """
        super(Dummy, self).__init__(conn, cursor)
        self.table_name = "dummies"
        self.field_map = FIELD_MAP
        self.setup()

    def __repr__(self):
        if self.id:
            return "<Dummy %s: %s>" % (self.id, self.name)
        elif self.name:
            return "<Dummy %s>" % (self.name)
        else:
            return "<Dummy>"


# End File: automox/pignus/src/pignus/utils/tests/mock_model_dummy.py
