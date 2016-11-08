from model import Model


class Users(Model):

    def get_or_create_user(self, user):
        try:
            insert = """
            INSERT INTO users (name, family_name, email)
            VALUES ('{0}', '{1}', '{2}')
            """.format(user['given_name'], user['family_name'], user['email'])

            self.db.execute(insert)
        except:  # TODO
            pass

        query = """
        SELECT uid FROM users WHERE email = '{0}'
        """.format(user['email'])

        result = self.db.execute(query)
        return self.deproxy(result)[0]['uid']

    def is_valid_uni(self, uni):
        uni = self.escape_string(uni)
        query = "select sid from students where uni = '%s'" % uni
        result = self.db.execute(query)
        return True if result.rowcount == 1 else False
