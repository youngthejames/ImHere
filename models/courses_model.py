from model import Model
from datetime import datetime, date


class Courses(Model):

    def __init__(self, dbconn, cid):
        Model.__init__(self, dbconn)
        self.cid = cid

    def get_course_name(self):
        query = 'select name from courses where cid = %s' % self.cid
        result = self.db.execute(query)
        return result.fetchone()[0]

    def get_students(self):
        query = ('select name, family_name, email '
                 'from users, enrolled_in '
                 'where users.uid = enrolled_in.sid '
                 'and enrolled_in.cid = %s'
                 % self.cid)
        result = self.db.execute(query)
        return self.deproxy(result)

    def add_student(self, uni):
        query = "select sid from students where uni = '%s'" % uni 
        result = self.db.execute(query)

        if result.rowcount == 1:
            # found a student with uni, attempt to add to enrolled_in
            sid = result.fetchone()[0]
            try:
                query = 'insert into enrolled_in values (%s, %s)' \
                        % (sid, self.cid)
                self.db.execute(query)
            except:
                # failed because already in enrolled_in
                pass
        else:
            # invalid uni, ignoring
            pass

    def remove_student(self, uni):
        query = "select sid from students where uni = '%s'" % uni
        result = self.db.execute(query)

        if result.rowcount == 1:
            # found a student with uni, attempt to remove from enrolled_in
            sid = result.fetchone()[0]
            try:
                query = 'delete from enrolled_in where sid = %s and cid = %s' \
                        % (sid, self.cid)
                self.db.execute(query)
                #TODO: delete all attendance records of student
            except:
                # failed because it was not in enrolled_in to begin with
                pass
        else:
            # invalid uni, ignoring
            pass
