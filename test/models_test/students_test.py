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

    dave_courses = dave.get_courses()

    jaina = students_model.Students(db, 6)

    jaina_courses = jaina.get_courses()
    assert len(jaina_courses) == 0
