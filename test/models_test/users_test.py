
from models import users_model

def test_get_create(db):
    user = {
        'given_name': 'Leeroy',
        'family_name': 'Jenkins',
        'email': 'lj1337@columbia.edu'
    }

    um = users_model.Users(db)

    # create a user
    uid = um.get_or_create_user(user)

    assert type(uid) is int
    assert uid > 0

    # second call is to get that user
    uid2 = um.get_or_create_user(user)
    assert uid == uid2

def test_is_valid_uni(db):

    um = users_model.Users(db)

    assert not um.is_valid_uni('thisisobviouslyfake')
