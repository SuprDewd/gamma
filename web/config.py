import os
import sys
from tornado.options import define

DIR_NAME = os.path.realpath(os.path.dirname(__file__))
_libs = set([DIR_NAME])
for (path, dirs, files) in os.walk(os.path.join(DIR_NAME, 'libs')):
    if '__init__.py' in files:
        _libs.add(os.path.realpath(os.path.join(DIR_NAME, 'libs', path, '..')))

sys.path = list(_libs) + sys.path

define('port', default=8888, help='run on the given port', type=int)
define('debug', default=False, type=bool)
define('db_path', default='sqlite://', type=str)
define('local', default=False, type=bool)
