import os
import logging
from config import *
import tornado.web
from tornado.options import options
from tornado.web import url
import tornado.httpserver
import tornado.ioloop
from handlers import *

class GammaWeb(tornado.web.Application):
    def __init__(self):

        handlers = [
            url('/', IndexHandler, name='index')
        ]

        cur_dir = os.path.dirname(__file__)

        settings = dict(
            debug = options.debug,
            static_path = os.path.join(cur_dir, 'static'),
            template_path = os.path.join(cur_dir, 'templates'),
            xsrf_cookies = True,
            cookie_secret = 'fP#91c.e+8jMqie+fZN!Oc*LABaMGl/PSUyTZhgx87+=@yepwcXN.kW'
        )

        tornado.web.Application.__init__(self, handlers, **settings)
        logger = logging.getLogger()

        if options.debug:
            logger.setLevel(logging.DEBUG)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(GammaWeb())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
