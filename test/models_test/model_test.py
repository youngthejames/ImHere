import sqlalchemy
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
