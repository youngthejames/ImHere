from models import index_model

def test_is_student(db):
    real_student = {
        'sid': '3',
        'uni': 'ds9876'
    }
    im = index_model.Index(db, real_student['sid']) 
    assert im.is_student() is True

    fake_student = {
        'sid': '-444',
        'uni': 'qwerty'
    }
    im = index_model.Index(db, fake_student['sid'])
    assert im.is_student() is False


def test_is_teacher(db):
    real_teacher = {
        'tid': '4'
    }
    im = index_model.Index(db, real_teacher['tid'])
    assert im.is_teacher() is True

    fake_teacher = {
        'tid': '-443',
    }
    im = index_model.Index(db, fake_teacher['tid'])
    assert im.is_teacher() is False
