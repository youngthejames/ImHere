from models import students_model
from models import courses_model


def test_get_uni(db):
    sm = students_model.Students(db, 3)
    assert sm.get_uni() == 'ds9876'


def test_get_courses(db):
    dave = students_model.Students(db, 3)

    dave_courses = dave.get_courses()
    assert len(dave_courses) == 1
    art = dave_courses[0]
    assert art['cid'] == 4
    assert art['name'] == 'Art History'

    cm_running = courses_model.Courses(db, 1)
    cm_running.add_student('ds9876')

    dave_courses = dave.get_courses()
    assert len(dave_courses) == 2
    running = dave_courses[0]
    assert running['cid'] == 1
    assert running['name'] == 'Running'
    art = dave_courses[1]
    assert art['cid'] == 4
    assert art['name'] == 'Art History'

    jaina = students_model.Students(db, 6)

    jaina_courses = jaina.get_courses()
    assert len(jaina_courses) == 0


def test_get_secret_and_seid(db):
    dave = students_model.Students(db, 3)
    secret, seid = dave.get_secret_and_seid()
    assert secret == '0000'
    assert seid == 2

    jaina = students_model.Students(db, 6)
    secret, seid = jaina.get_secret_and_seid()
    assert secret is None
    assert seid == -1


def test_has_signed_in(db):
    dave = students_model.Students(db, 3)
    assert dave.has_signed_in()

    grommash = students_model.Students(db, 5)
    assert not grommash.has_signed_in()


def test_insert_attendance_record(db):
    grommash = students_model.Students(db, 5)
    assert not grommash.has_signed_in()

    # insert grommash into session (seid=2)
    grommash.insert_attendance_record(2)

    assert grommash.has_signed_in()


def test_get_num_attendance_records(db):
    jaina = students_model.Students(db, 6)
    cid_of_ah = 4

    assert jaina.get_num_attendance_records(cid_of_ah) == 0

    # insert into 1st session
    jaina.insert_attendance_record(1)

    assert jaina.get_num_attendance_records(cid_of_ah) == 1

    # insert into 2nd session
    jaina.insert_attendance_record(2)

    assert jaina.get_num_attendance_records(cid_of_ah) == 2
