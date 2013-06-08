#!/usr/bin/python2
from config import *
import os
import logging
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.locale
from tornado.options import options
from tornado.web import url
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from handlers import *
import models
import ui_modules
import test_data

class GammaWeb(tornado.web.Application):
    def __init__(self):

        handlers = [

            # Index
            url('/',                                             IndexHandler),

            # Contests
            url('/contests/?',                                   AllContestsHandler),
            url('/contests/([0-9]+)/?',                          AllContestsHandler),
            url('/contest/([0-9]+)/?',                           ContestHandler),
            url('/contest/([0-9]+)/register/?',                  ContestRegisterHandler),
            url('/contest/([0-9]+)/scoreboard/?',                ScoreboardHandler),
            url('/contest/([0-9]+)/problem/([^/]+)/?',           ProblemHandler),
            url('/contest/([0-9]+)/problem/([^/]+)/comments/?',  CommentsHandler),

            # Problems
            url('/problems/?',                                   AllProblemsHandler),
            url('/problems/([0-9]+)/?',                          AllProblemsHandler),
            url('/problem/([^/]+)/?',                            ProblemHandler),
            url('/problem/([^/]+)/comments/?',                   CommentsHandler),

            # Users
            url('/user/register/?',                              RegisterHandler),
            url('/user/register/successful/?',                   RegisterSuccessfulHandler),
            url('/user/register/confirm/([^/]+)/?',              RegisterConfirmHandler),
            url('/user/login/?',                                 LoginHandler),
            url('/user/logout/?',                                LogoutHandler),

            # Admin
            url('/admin/?',                                      AdminHandler),
        ]

        cur_dir = os.path.dirname(__file__)
        tornado.locale.load_translations(os.path.join(cur_dir, 'translations'))

        settings = dict(
            debug = options.debug,
            static_path = os.path.join(cur_dir, 'static'),
            template_path = os.path.join(cur_dir, 'templates'),
            xsrf_cookies = True,
            cookie_secret = 'fP#91c.e+8jMqie+fZN!Oc*LABaMGl/PSUyTZhgx87+=@yepwcXN.kW',
            ui_modules = ui_modules.modules,
        )

        tornado.web.Application.__init__(self, handlers, **settings)
        db_engine = create_engine(options.db_path, convert_unicode=True, echo=options.debug)
        models.Base.metadata.create_all(db_engine)
        self.db = scoped_session(sessionmaker(bind=db_engine))

        logger = logging.getLogger()
        if options.debug:
            logger.setLevel(logging.DEBUG)

        if options.local:
            test_data.add_test_data(self.db)

    def _init_db(self):
        sess = self.db()
        # TODO: initialize db


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(GammaWeb())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
