from model import Model
from datetime import datetime, date


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
        course_name = self.escape_string(course_name)
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
        cid = self.escape_string(cid)
        query = 'delete from courses where cid = %s' % cid
        self.db.execute(query)
