import pytest
import sqlalchemy

@pytest.fixture(scope="module")
def db():
    db = sqlalchemy.create_engine(('postgres://'
                            'cwuepekp:SkVXF4KcwLJvTNKT41e7ruWQDcF3OSEU'
                            '@jumbo.db.elephantsql.com:5432'
                            '/cwuepekp'),
                            pool_size=1)
    connection = db.connect()
    yield connection

    connection.close()
