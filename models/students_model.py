from model import Model

class Students(Model):

    def __init__(self, dbconn, sid):
        Model.__init__(self, dbconn)
        self.sid = sid

    def get_classes(self):
        query = ('select courses.cid, courses.name, courses.start_time, '
                 'courses.end_time, courses.start_date, courses.end_date, '
                 'courses.day, courses.active, enrolled_in.sid '
                 'from courses, enrolled_in '
                 'where courses.cid = enrolled_in.cid '
                 'and enrolled_in.sid = %s'
                 % self.sid)

        result = self.db.execute(query)
        return self.deproxy(result)

