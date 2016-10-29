from model import Model


class Index(Model):

    def __init__(self, dbconn, uid):
        Model.__init__(self, dbconn)
        self.uid = uid

    def is_student(self):
        query = 'select * from students where sid = %s' % self.uid
        result = self.db.execute(query)
        return True if result.rowcount == 1 else False

    def is_teacher(self):
        query = 'select * from teachers where tid = %s' % self.uid
        result = self.db.execute(query)
        return True if result.rowcount == 1 else False
