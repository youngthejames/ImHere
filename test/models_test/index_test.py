from models import index_model

real_student = {
    'sid': '3',
    'uni': 'ds9876'
}
fake_student = {
    'sid': '-444',
    'uni': 'qwerty'
}

real_teacher = {
    'tid': '4'
}
fake_teacher = {
    'tid': '-443',
}


def test_is_student(db):
    im = index_model.Index(db, real_student['sid'])
    assert im.is_student() is True

    im = index_model.Index(db, fake_student['sid'])
    assert im.is_student() is False

    im = index_model.Index(db, real_teacher['tid'])
    assert im.is_student() is False


def test_is_teacher(db):

    im = index_model.Index(db, real_teacher['tid'])
    assert im.is_teacher() is True

    im = index_model.Index(db, fake_teacher['tid'])
    assert im.is_teacher() is False

    im = index_model.Index(db, real_student['sid'])
    assert im.is_teacher() is False
