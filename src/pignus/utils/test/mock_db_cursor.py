"""Mock Db Cursor

"""
from datetime import datetime


class MockDbCursor:

    def execute(*args, **kwargs) -> bool:
        return True

    def lastrowid(**kwargs):
        return None

    def fetchone(*args, **kwargs):
        return [
            1,
            datetime(2021, 1, 1),
            None,
            True,
            "hello world",
            6,
            datetime(2021, 1, 2),
            False,
            "one,two,three"
        ]

    def fetchall(self):
        return True

# End File: automox/pignus/src/pignus/utils/tests/mock_db_cursor.py
