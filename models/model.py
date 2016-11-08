class Model:

    def __init__(self, dbconn):
        self.db = dbconn

    # transform the sqlalchemy ResultProxy into a python list
    def deproxy(self, resultproxy):

        result = []
        for row in resultproxy:
            result.append(row)

        return result

    def escape_string(self, input):
        if type(input) is str or type(input) is unicode:
            return input.replace("'", "''")
        else:
            return input
