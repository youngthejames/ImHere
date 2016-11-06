import pytest
import sqlalchemy

import test.db_util

@pytest.fixture(scope="module")
def db():
    test_db = test.db_util.create_test_db()

    conn = test_db[0].connect()
    yield conn

    conn.close()

    test.db_util.destroy_test_db(test_db[1])
