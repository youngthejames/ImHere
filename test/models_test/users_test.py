from models import users_model


def test_get_create(db):
    user = {
        'given_name': 'Jack',
        'family_name': 'Sparrow',
        'email': 'js1234@columbia.edu'
    }

    um = users_model.Users(db)

    # create a user
    uid = um.get_or_create_user(user)

    assert type(uid) is int
    assert uid > 0

    # second call is to get that user
    uid2 = um.get_or_create_user(user)
    assert uid == uid2

    # test that an existing user is fetched correctly
    user = {
        'given_name': 'Leeroy',
        'family_name': 'Jenkins',
        'email': 'lj1337@columbia.edu'
    }

    uid3 = um.get_or_create_user(user)
    assert type(uid3) is int
    assert uid3 == 1


def test_is_valid_uni(db):

    um = users_model.Users(db)

    assert not um.is_valid_uni('thisisobviouslyfake')
    assert um.is_valid_uni('ds9876')
    assert not um.is_valid_uni('lj1337')


def test_sql_injection(db):
    um = users_model.Users(db)

    assert um.is_valid_uni("' or 1=1;") == False
    assert um.is_valid_uni("'little bobby tables'") == False
