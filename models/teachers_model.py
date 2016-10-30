from model import Model
from datetime import datetime, date
from random import randint


class Teachers(Model):

    def __init__(self, dbconn, tid):
        Model.__init__(self, dbconn)
        self.tid = tid
        self.now = datetime.time(datetime.now())
        self.today = date.today()

    def get_courses(self):
        query = ('select courses.cid, courses.name '
                 'from courses, teaches '
                 'where courses.cid = teaches.cid '
                 'and teaches.tid = %s'
                 % self.tid)
        result = self.db.execute(query)
        return self.deproxy(result)

    def get_courses_with_session(self):
        query = ('select courses.cid, name, active, secret '
                 'from teaches inner join courses on '
                 '(courses.cid = teaches.cid and '
                 'teaches.tid = %s) '
                 'left outer join sessions on '
                 '(courses.cid = sessions.cid '
                 "and sessions.expires > '%s' "
                 "and sessions.day >= '%s')"
                 % (self.tid, self.now, self.today))

        result = self.db.execute(query)
        return self.deproxy(result)

    def add_course(self, course_name):
        query = ('insert into courses (name, active) '
                 "values ('%s', 0) "
                 'returning cid'
                 % course_name)
        result = self.db.execute(query)
        cid = result.fetchone()[0]

        query = 'insert into teaches values (%s, %d)' % (self.tid, cid)
        self.db.execute(query)
        return cid

    def remove_course(self, cid):
        query = ('delete from teaches '
                 'where cid = %s '
                 'and tid = %s'
                 % (cid, self.tid))
        self.db.execute(query)

    def close_session(self, cid):
        query = ("update sessions set expires = '%s' "
                 'where sessions.cid = %s'
                 % (self.now, cid))
        self.db.execute(query)

        query = 'update courses set active = 0 where courses.cid = %s' % cid
        self.db.execute(query)

    def open_session(self, cid):
        # auto-generated secret code for now
        randsecret = randint(1000, 9999)
        query = ('insert into sessions (cid, secret, expires, day) '
                 "values (%s, '%d', '%s', '%s')"
                 % (cid, randsecret, '23:59:59', self.today))
        self.db.execute(query)

        query = 'update courses set active = 1 where courses.cid = %s' % cid
        self.db.execute(query)
