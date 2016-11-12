# CREATE USER tester with password 'mattsbigpassw0rrd';
import uuid
import sqlalchemy


def create_test_db():
    '''create a temporary database with complete schema and randomized name
    returns the database connection and name
    '''
    db = sqlalchemy.create_engine(
            'postgres://tester:mattsbigpassw0rrd@45.55.87.0:5432/postgres')
    conn = db.connect()
    conn.execute('commit')

    db_name = 'test' + str(uuid.uuid4().get_hex())

    q = 'create database {0}'.format(db_name)
    conn.execute(q)

    conn.close()

    c_string = 'postgres://tester:mattsbigpassw0rrd@45.55.87.0:5432/{0}'
    conn_string = c_string.format(db_name)
    db = sqlalchemy.create_engine(conn_string,
                                  poolclass=sqlalchemy.pool.NullPool)
    conn = db.connect()

    # create the schema
    schema = _read_sql_file('schema.sql')
    for q in schema:
        conn.execute(q)

    # put in some test data
    data = _read_sql_file('test/data.sql')
    for q in data:
        conn.execute(q)

    conn.close()

    return (db, db_name)


# sqalchemy sucks and can only execute one command at a time
# this puts it in a format that will work with it....
def _read_sql_file(file):

    queries = []

    current = ''
    with open(file, 'r') as f:
        for line in f:
            if '--' in line:
                continue
            elif ';' in line:
                current += line.replace(';', '')
                queries.append(current)
                current = ''
            else:
                current += line + ' '
    return queries


def destroy_test_db(db_name):
    '''deletes a test db
    '''
    db = sqlalchemy.create_engine(
        'postgres://tester:mattsbigpassw0rrd@45.55.87.0:5432/postgres')
    conn = db.connect()
    conn.execute('commit')

    q = 'drop database {0}'.format(db_name)
    conn.execute(q)
    conn.close()
