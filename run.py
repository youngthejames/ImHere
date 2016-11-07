import os
import uuid
import sqlalchemy

import imhere

host = '0.0.0.0'
port = int(os.environ.get('PORT') or 4156)
print 'running on %s:%d' % (host, port)

db = sqlalchemy.create_engine(('postgres://'
                               'cwuepekp:SkVXF4KcwLJvTNKT41e7ruWQDcF3OSEU'
                               '@jumbo.db.elephantsql.com:5432'
                               '/cwuepekp'),
                              pool_size=5)
imhere.app.config['db'] = db

imhere.app.secret_key = str(uuid.uuid4())
imhere.app.run(host=host, port=port)
