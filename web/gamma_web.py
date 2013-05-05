import os
import logging
from config import *
import tornado.web
from tornado.options import options
from tornado.web import url
import tornado.httpserver
import tornado.ioloop
from handlers import *
import models

class GammaWeb(tornado.web.Application):
    def __init__(self):

        handlers = [

            # Index
            url('/',                                             IndexHandler),

            # Contests
            url('/contests/?',                                   AllContestsHandler),
            url('/contest/([0-9]+)/?',                           ContestHandler),
            url('/contest/([0-9]+)/scoreboard/?',                ScoreboardHandler),
            url('/contest/([0-9]+)/problem/([^/]+)/?',           ProblemHandler),
            url('/contest/([0-9]+)/problem/([^/]+)/solutions/?', SolutionHandler),

            # Problems
            url('/problems/?',                                   AllProblemsHandler),
            url('/problem/([^/]+)/?',                            ProblemHandler),
            url('/problem/([^/]+)/solutions/?',                  SolutionHandler),

            # Users
            url('/user/register/?',                              RegisterHandler),
            url('/user/register/confirm/([^/]+)/?',              RegisterConfirmHandler),
            url('/user/login/?',                                 LoginHandler),
            url('/user/logout/?',                                LogoutHandler),

            # Admin
            url('/admin/?',                                      AdminHandler),
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
        db_engine = create_engine(DB_PATH, convert_unicode=True, echo=options.debug)
        models.init_db(db_engine)
        self.db = scoped_session(engine=db_engine)

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
