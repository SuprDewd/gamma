import os
import sys

DIR_NAME = os.path.realpath(os.path.dirname(__file__))
sys.path.append(DIR_NAME)

from tornado.options import define

define('port', default=8888, help='run on the given port', type=int)
define('debug', default=False, type=bool)
define('db_path', default='sqlite://', type=str)
define('local', default=False, type=bool)
