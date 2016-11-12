import sqlalchemy
import pytest

from models import model


def test_deproxy(db):
    model_obj = model.Model(db)

    # selecting the 'Dave Student' user
    query = 'select * from users where uid = 3'
    result = db.execute(query)

    deproxy_list = model_obj.deproxy(result)

    assert type(deproxy_list) is list
    assert type(deproxy_list[0]) is sqlalchemy.engine.result.RowProxy
    assert len(deproxy_list) == 1


def test_escape_string(db):
    model_obj = model.Model(db)

    query = "select * from users where email = '{0}'"

    safe = model_obj.escape_string("matt@brogrammers.co.nr")
    danger = model_obj.escape_string("dave '; drop table users;")

    try:
        db.execute(query.format(safe))
    except:
        pytest.fail('query syntax' + safe)

    try:
        db.execute(query.format(danger))
    except:
        pytest.fail('query syntax' + danger)
