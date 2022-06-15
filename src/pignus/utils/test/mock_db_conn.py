"""Mock Db Conn

"""


class MockDbConn:

    def commit(self, **kwargs) -> bool:
        return True

# End File: automox/pignus/src/pignus/utils/tests/mock_db_conn.py
