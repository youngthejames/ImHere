class Model:

    def __init__(self, dbconn):
        self.db = dbconn

    # transform the sqlalchemy ResultProxy into a python list
    def deproxy(self, resultproxy):

        result = []
        for row in resultproxy:
            result.append(row)

        return result
