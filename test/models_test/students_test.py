from models import students_model

def test_get_uni(db):
    sm = students_model.Students(db, 3)

    assert sm.get_uni() == 'ds9876'

def test_get_courses(db):
    dave = students_model.Students(db, 3)

    dave_courses = dave.get_courses()
    assert len(dave_courses) == 1

    jaina = students_model.Students(db, 6)

    jaina_courses = jaina.get_courses()
    assert len(jaina_courses) == 0
