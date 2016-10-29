from model import Model
from datetime import datetime, date


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

    def get_secret_and_seid(self):
        now = datetime.time(datetime.now())
        today = date.today()

        query = ('select seid '
                 'from sessions, enrolled_in '
                 'where enrolled_in.sid = %s '
                 'and enrolled_in.cid = sessions.cid '
                 "and sessions.expires > '%s' "
                 "and sessions.day >= '%s'"
                 % (self.sid, now, today))
        result = self.db.execute(query)
        seid = result.fetchone()[0]

        query = 'select secret from sessions where seid = %s' % seid
        result = self.db.execute(query)
        secret = result.fetchone()[0]

        return secret, seid

    def insert_attendance_record(self, seid):
        query = 'insert into attendance_records values (%s, %s)' \
                % (self.sid, seid)
        self.db.execute(query)
