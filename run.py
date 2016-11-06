
import os
import uuid

import imhere

host = '0.0.0.0'
port = int(os.environ.get('PORT') or 4156)
print 'running on %s:%d' % (host, port)

imhere.app.secret_key = str(uuid.uuid4())
imhere.app.run(host=host, port=port)
