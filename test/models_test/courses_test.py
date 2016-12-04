from models import courses_model
from models import students_model


def test_get_course_name(db):
    cm = courses_model.Courses(db, 4)  # art history
    name = cm.get_course_name()

    assert name == 'Art History'


def test_get_students(db):
    cm = courses_model.Courses(db, 4)  # art history
    student_list = cm.get_students()

    assert type(student_list) is list
    assert len(student_list) == 2

    assert 3 in student_list[0].items()[0]
    assert 'Dave' in student_list[0].items()[1]
    assert 'Student' in student_list[0].items()[2]
    assert 'ds9876@columbia.edu' in student_list[0].items()[3]

    assert 5 in student_list[1].items()[0]
    assert 'Grommash' in student_list[1].items()[1]
    assert 'Hellscream' in student_list[1].items()[2]
    assert 'gh1234@columbia.edu' in student_list[1].items()[3]


def test_add_student(db):
    cm = courses_model.Courses(db, 4)  # art history

    # check length before
    student_list = cm.get_students()
    assert len(student_list) == 2

    # check for a valid add_student call
    add_student_result = cm.add_student('jp9122')  # adding Jaina Proudmoore
    assert add_student_result == 0

    # check length after
    student_list = cm.get_students()
    assert len(student_list) == 3

    # check for adding a student already in the class
    add_student_result = cm.add_student('jp9122')
    assert add_student_result == -2

    # check length to make sure it remains
    student_list = cm.get_students()
    assert len(student_list) == 3

    # check for adding a non-existent student
    add_student_result = cm.add_student('nonexistent')
    assert add_student_result == -1

    # check length to make sure it remains
    student_list = cm.get_students()
    assert len(student_list) == 3


def test_remove_student(db):
    cm = courses_model.Courses(db, 4)  # art history

    # check length before (Jaina now in class)
    student_list = cm.get_students()
    assert len(student_list) == 3

    # check for a valid remove_student call
    remove_student_result = cm.remove_student('jp9122')  # removing Jaina
    assert remove_student_result == 0

    # check length after valid remove
    student_list = cm.get_students()
    assert len(student_list) == 2

    # check for removing a student not in the class
    remove_student_result = cm.remove_student('jp9122')
    assert remove_student_result == -3

    # check length to make sure it remains the same
    student_list = cm.get_students()
    assert len(student_list) == 2

    # check for removing a nonexistent student
    remove_student_result = cm.remove_student('nonexistent')
    assert remove_student_result == -1

    # check length to make sure it remains the same
    student_list = cm.get_students()
    assert len(student_list) == 2

    ###########################################################################
    # now test that remove_student takes away attendance records
    # testing with Dave, who has an AR in an old session of art history
    query = ('select * from attendance_records '
             'where sid = %s'
             % 3)
    result = db.execute(query)
    assert result.rowcount == 2  # Dave is in two sessions of this course

    # now remove Dave
    cm.remove_student('ds9876')

    result = db.execute(query)
    assert result.rowcount == 0


def test_get_active_session(db):
    cm = courses_model.Courses(db, 4)  # art history
    seid = cm.get_active_session()
    assert seid == 2

    cm = courses_model.Courses(db, 1)  # running, no active session
    seid = cm.get_active_session()
    assert seid == -1


def test_close_session(db):
    cm = courses_model.Courses(db, 4)  # art history, has open session

    seid = cm.get_active_session()
    assert seid == 2

    cm.close_session(seid)

    # checking if seid is -1 for same class that was just open
    seid = cm.get_active_session()
    assert seid == -1


def test_open_session(db):
    cm = courses_model.Courses(db, 1)  # running, no active session

    seid = cm.get_active_session()
    assert seid == -1  # no active session

    cm.open_session()

    seid = cm.get_active_session()
    assert seid != -1


def test_get_secret_code(db):
    cm = courses_model.Courses(db, 2)  # writing, has no active session

    seid = cm.get_active_session()
    assert seid == -1  # make sure no active session exists

    randsecret = cm.open_session()
    seid = cm.get_active_session()
    assert seid != -1  # make sure an active session exists now

    secret = cm.get_secret_code()
    assert randsecret == secret
    assert secret is not None

    cm.close_session(seid)
    secret = cm.get_secret_code()
    assert secret is None


def test_get_num_sessions(db):
    cm = courses_model.Courses(db, 3)  # german 3, has no sessions
    num_sessions = cm.get_num_sessions()
    assert num_sessions == 0

    cm = courses_model.Courses(db, 4)  # art history, has 2 sessions
    num_sessions = cm.get_num_sessions()
    assert num_sessions == 2


def test_sql_injection(db):
    cm = courses_model.Courses(db, 1)

    assert cm.add_student("' or 1=1;") == -1
    assert cm.add_student("'little bobby tables'") == -1

    assert cm.remove_student("' or 1=1;") == -1
    assert cm.remove_student("'little bobby tables'") == -1

def test_add_teacher(db):
    cm = courses_model.Courses(db, 6) # test_add_teacher course

    teachers = cm.get_teachers()
    assert len(teachers) == 1
    assert teachers[0]['email'] == 'add@teacher.com'

    # insert a fake user
    result = cm.add_teacher('fake@email.com')
    assert result[0] == False
    assert 'User fake@email.com not found' in result[1]

    # insert a user that isn't a teacher
    result = cm.add_teacher('nota@teacher.com')
    assert result[0] == True

    #insert a user that is a teacher
    result = cm.add_teacher('isa@teacher.com')
    assert result[0] == True

    teachers = cm.get_teachers()
    assert len(teachers) == 3

    cm.remove_teacher(11)
    teachers = cm.get_teachers()
    assert len(teachers) == 2

def test_sessions(db):

    cid = 7
    student = 15

    cm = courses_model.Courses(db, cid)
    sm = students_model.Students(db, student)

    sessions = cm.get_sessions()
    assert len(sessions) == 0

    secret = cm.open_session()
    seid = cm.get_active_session()

    sessions = cm.get_sessions()
    assert len(sessions) == 1
    assert sessions[0]['enrollment'] == 1
    assert sessions[0]['attendance'] == 0

    sm.insert_attendance_record(seid)
    sessions = cm.get_sessions()
    assert sessions[0]['attendance'] == 1
