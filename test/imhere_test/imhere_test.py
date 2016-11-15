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

newt = {
    'family_name': 'Teacher',
    'name': 'New Teacher',
    'email': 'newt@cs.columbia.edu',
    'given_name': 'New'
}
newt_id = 7

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

def test_teacher_session_manage(db):

    with imhere.app.test_client() as c:

        with c.session_transaction() as sess:
            login(sess, newt, newt_id)
            sess['is_teacher'] = True

        res = c.get('/teacher/')
        assert 'Writing' in res.data
        assert 'Open Attendance Window' in res.data
        assert 'Secret Code' not in res.data

        payload = {'open': 2}
        res = c.post('/teacher/', data=payload)
        assert 'Close Attendance Window' in res.data
        assert 'Secret Code' in res.data

        payload = {'close': 2}
        res = c.post('/teacher/', data=payload)
        assert 'Open Attendance Window' in res.data
        assert 'Secret Code' not in res.data

def test_teacher_add_class(db):

    with imhere.app.test_client() as c:

        # first lets test this page is properly gated
        res = c.get('/teacher/add_class')
        assert 302 == res.status_code

        with c.session_transaction() as sess:
            login(sess, newt, newt_id)

        res = c.get('/teacher/add_class')
        assert 302 == res.status_code

        with c.session_transaction() as sess:
            sess['is_teacher'] = True

        res = c.get('/teacher/add_class')
        assert 'Create a Class' in res.data
        assert 'Student Unis' in res.data
        assert 200 == res.status_code

        payload = {'unis': [''], 'classname': 'newts variety hour'}
        res = c.post('/teacher/add_class', data=payload, follow_redirects=True)
        assert 'newts variety hour' in res.data
        assert 'Add a Class' in res.data
        assert 200 == res.status_code

        payload = {'unis': ['fake'], 'classname': 'newts big class'}
        res = c.post('/teacher/add_class', data=payload)
        assert "Invalid UNI's entered, please recreate the class" in res.data

        payload = {'unis': ['sw1234'], 'classname': 'newts big class'}
        res = c.post('/teacher/add_class', data=payload, follow_redirects=True)
        assert 'newts big class' in res.data
        assert 'Add a Class' in res.data
        assert 200 == res.status_code

        # was sylvanas added to this class?
        query = "SELECT courses.cid, courses.name FROM courses JOIN enrolled_in ON courses.cid = enrolled_in.cid WHERE enrolled_in.sid = 8 AND courses.name = 'newts big class'"
        res = db.execute(query)
        assert res.rowcount == 1

def test_teacher_remove_class(db):

    with imhere.app.test_client() as c:

        # first check page is auth protected

        res = c.get('/teacher/remove_class')
        assert 302 == res.status_code

        with c.session_transaction() as sess:
            login(sess, newt, newt_id)

        res = c.get('/teacher/remove_class')
        assert 302 == res.status_code

        with c.session_transaction() as sess:
            sess['is_teacher'] = True

        res = c.get('/teacher/remove_class')
        assert 'Class List' in res.data
        assert 'Remove Class' in res.data
        assert 'Newts big blunder' in res.data
        assert 200 == res.status_code

        payload = {'cid': 5}
        res = c.post('/teacher/remove_class', data=payload, follow_redirects=True)
        assert 'Add a Class' in res.data
        assert 'Newts big blunder' not in res.data
        assert 200 == res.status_code

def test_teacher_view_class(db):

    with imhere.app.test_client() as c:

        with c.session_transaction() as sess:
            login(sess, newt, newt_id)
            sess['is_teacher'] = True

        query = "select cid from courses where name = 'newts big class'"
        cursor = db.execute(query)
        for item in cursor:
            cid = item[0]
        #test basic display
        payload = {'cid': cid}
        res = c.post('/teacher/view_class', data=payload)
        assert 'newts big class' in res.data
        assert 'sw1234' in res.data
        #test removing students
        payload = {'cid': cid, 'remove_student': 'sw1234'}
        res = c.post('/teacher/view_class', data=payload)
        assert 'sw1234' not in res.data
        res = c.post('/teacher/view_class', data=payload)
        #assert 'sw1234 is not in the class to begin with' in res.data
        #test adding students
        payload = {'cid': cid, 'add_student': 'sw1234'}
        res = c.post('/teacher/view_class', data=payload)
        assert 'sw1234' in res.data
        #test error message
        payload = {'cid': cid, 'add_student': 'sw1234'}
        res = c.post('/teacher/view_class', data=payload)
        #assert 'sw1234 is already in the class' in res.data
        payload = {'cid': cid, 'open': cid}
        res = c.post('/teacher/view_class', data=payload)
        assert 'Secret Code' in res.data
        payload = {'cid': cid, 'close': cid}
        res = c.post('/teacher/view_class', data=payload)
        assert 'Secret Code' not in res.data


unreg = {
        'family_name': 'User',
        'name': 'Unregistered User',
        'email': 'uu0000@columbia.edu',
        'given_name': 'Unregistered'
    }
unreg_id = 9


def test_register(db):


    # should be gated by sso
    with imhere.app.test_client() as c:
        res = c.get('/register')
        assert 302 == res.status_code

        with c.session_transaction() as sess:
            login(sess, unreg, unreg_id)

        res = c.get('/register')
        assert 'Registration' in res.data
        assert 'I am a' in res.data
        assert 200 == res.status_code

        # give bad uni
        payload = {'type': 'student', 'uni': 'ds9876'}
        res = c.post('/register', data=payload)
        assert 'UNI already in use' in res.data
        with c.session_transaction() as sess:
            assert sess['is_student'] == False

        payload = {'type': 'student', 'uni': 'uu0000'}
        res = c.post('/register', data=payload, follow_redirects=True)
        assert 'Registration' not in res.data
        assert 200 == res.status_code
        with c.session_transaction() as sess:
            assert sess['is_student'] == True

        res = c.get('/register')
        assert 'You are already registered as a student' in res.data

        payload = {'type': 'teacher'}
        res = c.post('/register', data=payload, follow_redirects=True)
        assert 'Registration' not in res.data
        assert 'Add a Class' in res.data
        with c.session_transaction() as sess:
            assert sess['is_teacher'] == True

        res = c.get('/register')
        assert 'You are already registered as a student AND as a teacher' in res.data

def test_main_student(db):
    with imhere.app.test_client() as c:
        res = c.get('/student/')
        assert 302 == res.status_code

        with c.session_transaction() as sess:
            login(sess, unreg, unreg_id)
            sess['is_teacher'] = False
            sess['is_student'] = True

        res = c.get('/student/')
        assert 'Student View' in res.data
