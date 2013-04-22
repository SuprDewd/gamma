import os
import sys

DIR_NAME = os.path.dirname(__file__)

sys.path.append(DIR_NAME)
sys.path.append(os.path.join(DIR_NAME, 'libs'))

from tornado.options import define

define('port', default=8888, help='run on the given port', type=int)
define('debug', default=False, type=bool)
define('db_path', default='sqlite://', type=str)
