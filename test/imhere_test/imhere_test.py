import flask
import pytest
import uuid

import imhere
import test.db_util

teacher_user = {
    'family_name': 'Teacher',
    'name': 'Douglas Teacher',
    'email': 'dougs@cs.columbia.edu',
    'given_name': 'Douglas'
}
teacher_user_id = 4


@pytest.yield_fixture(scope="module")
def db():
    test_db = test.db_util.create_test_db()

    imhere.app.config['db'] = test_db[0]
    imhere.app.secret_key = str(uuid.uuid4())

    conn = test_db[0].connect()
    yield conn

    conn.close()

    test.db_util.destroy_test_db(test_db[1])

def login(sess, user, userid):
    sess['credentials'] = 'blah'
    sess['google_user'] = user
    sess['id'] = userid
    sess['is_student'] = False
    sess['is_teacher'] = False

def test_index(db):
    with imhere.app.test_client() as c:
        res = c.get('/')
        assert 'ImHere' in res.data
        assert 'Login' in res.data
        assert 'Register' in res.data
        assert 200 == res.status_code


def test_teacher(db):

    with imhere.app.test_client() as c:

        # teacher page gated
        res = c.get('/teacher/')
        assert 302 == res.status_code

        # redirects to index
        res = c.get('/teacher/', follow_redirects=True)
        assert 'Login' in res.data
        assert 'Register' in res.data
        assert 200 == res.status_code

        # lets login
        with c.session_transaction() as sess:
            login(sess, teacher_user, teacher_user_id)

        # not a teacher so still gated
        res = c.get('/teacher/')
        assert 302 == res.status_code

        # login as teacher
        with c.session_transaction() as sess:
            sess['is_teacher'] = True

        # see the teacher page
        res = c.get('/teacher/')
        assert 'Add a Class' in res.data
        assert 'Logout' in res.data
        assert 200 == res.status_code

        # logout, again teacher page is gated
        c.get('/oauth/logout')
        res = c.get('/teacher/')
        assert 302 == res.status_code
