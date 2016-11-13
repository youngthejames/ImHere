import sqlalchemy
from models import teachers_model


def test_get_courses(db):
    douglas = teachers_model.Teachers(db, 4)

    courses_list = douglas.get_courses()

    assert len(courses_list) == 1
    assert type(courses_list) is list

    # len of 2 because we're selecting courses.cid and courses.name
    assert len(courses_list[0]) == 2
    assert type(courses_list[0]) is sqlalchemy.engine.RowProxy

    # check for each key that we selected
    rowproxy = courses_list[0]
    assert 'cid' in rowproxy
    assert 'name' in rowproxy
    assert 'notselected' not in rowproxy


def test_get_courses_with_session(db):
    douglas = teachers_model.Teachers(db, 4)

    courses_list_with_session = douglas.get_courses_with_session()

    assert len(courses_list_with_session) == 1
    assert type(courses_list_with_session) is list

    # len of 4 because we're selecting courses.cid, name, active, secret
    assert len(courses_list_with_session[0]) == 4
    assert type(courses_list_with_session[0]) is sqlalchemy.engine.RowProxy

    # check for each key that we selected
    rowproxy = courses_list_with_session[0]
    assert 'cid' in rowproxy
    assert 'name' in rowproxy
    assert 'active' in rowproxy
    assert 'secret' in rowproxy

    assert ('active', 1) in rowproxy.items()
    assert ('secret', '0000') in rowproxy.items()


def test_add_course(db):
    douglas = teachers_model.Teachers(db, 4)

    assert len(douglas.get_courses()) == 1

    cid = douglas.add_course('Mining')

    query = 'SELECT MAX(cid) from courses'
    res = db.execute(query)
    blah = []
    for b in res:
        blah.append(b)
    assert cid == blah[0]['max']
    # assert cid == 5  # next available cid

    assert len(douglas.get_courses()) == 2


def test_remove_course(db):
    douglas = teachers_model.Teachers(db, 4)

    assert len(douglas.get_courses()) == 2

    # remove mining class
    query = 'SELECT MAX(cid) from courses'
    res = db.execute(query)
    blah = []
    for b in res:
        blah.append(b)
    mining_cid = blah[0]['max']
    
    douglas.remove_course(mining_cid)
    assert len(douglas.get_courses()) == 1

    # remove imaginary class
    douglas.remove_course(-1)
    assert len(douglas.get_courses()) == 1
