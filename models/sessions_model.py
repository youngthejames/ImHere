from model import Model

class Sessions(Model):

    def __init__(self, dbconn, seid):
        Model.__init__(self, dbconn)
        self.seid = seid

    def get_session(self):
        query = '''
            SELECT s.seid, s.day, s.cid, COALESCE(ar.attendance, 0) as attendance,
              COALESCE((SELECT count(*) FROM enrolled_in e WHERE e.cid = s.cid), 0) AS enrollment,
              (SELECT name from courses WHERE courses.cid = s.cid) as name
            FROM sessions s LEFT OUTER JOIN (
              SELECT seid, count(sid) AS attendance
              FROM attendance_records
              GROUP BY seid) ar ON ar.seid = s.seid
            WHERE s.seid = %s
        ''' % (self.seid)

        result = self.db.execute(query)
        return self.deproxy(result)

    def get_attendance_record(self):
        query = '''
            SELECT se.sid, a.sid as present, c.message, c.status, u.name, u.email, u.uid
            FROM
              (SELECT e.sid
                FROM sessions s, enrolled_in e
                WHERE s.cid = e.cid AND s.seid = {0}) se
              LEFT OUTER JOIN
                (select * from attendance_records a2 where a2.seid = {0}) a ON a.sid = se.sid
              LEFT OUTER JOIN
                (select * from change_requests c2 where c2.seid = {0}) c ON c.sid = se.sid,
              users u
            WHERE u.uid = se.sid;
        '''.format(self.seid)

        result = self.db.execute(query)
        return self.deproxy(result)

    def remove_attendance_record(self, sid):
        query = '''
            DELETE FROM attendance_records WHERE sid=%s and seid=%s
        ''' % (sid, self.seid)

        self.db.execute(query)

    def delete_session(self):
        query = 'DELETE FROM sessions WHERE seid = %s' % (self.seid)
        self.db.execute(query)
