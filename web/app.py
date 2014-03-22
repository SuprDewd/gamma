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
            url('/contests',                                     AllContestsHandler,              name='contests'),
            url('/contest/([0-9]+)',                             ContestHandler,                  name='contest'),
            url('/contest/([0-9]+)/register',                    ContestRegisterHandler,          name='contest_register'),
            url('/contest/([0-9]+)/registered',                  ContestRegisteredHandler,        name='contest_registered'),
            url('/contest/([0-9]+)/standings',                   ContestStandingsHandler,         name='contest_standings'),
            url('/contest/([0-9]+)/submissions',                 ContestSubmissionsHandler,       name='contest_all_submissions'),
            url('/contest/([0-9]+)/submissions/([0-9]+)',        ContestSubmissionsHandler,       name='contest_team_submissions'),
            url('/contest/([0-9]+)/problem/([^/]+)',             ContestProblemHandler,           name='contest_problem'),
            url('/contest/([0-9]+)/problem/([^/]+)/comments',    CommentsHandler,                 name='contest_problem_comments'),

            # Problems
            url('/problems',                                     AllProblemsHandler,              name='problems'),
            url('/problem/([^/]+)',                              ProblemHandler,                  name='problem'),
            url('/problem/([^/]+)/comments',                     CommentsHandler,                 name='problem_comments'),

            # Users
            url('/user/register',                                UserRegisterHandler,             name='user_register'),
            url('/user/register/successful',                     UserRegisterSuccessfulHandler,   name='user_register_successful'),
            url('/user/register/confirm/([^/]+)',                UserRegisterConfirmHandler,      name='user_register_confirm'),
            url('/user/login',                                   UserLoginHandler,                name='user_login'),
            url('/user/logout',                                  UserLogoutHandler,               name='user_logout'),
            url('/user/home/profile',                            UserProfileHandler,              name='user_profile'),
            url('/user/home/password',                           UserPasswordHandler,             name='user_password'),
            url('/user/home/inbox',                              UserInboxHandler,                name='user_inbox'),
            url('/user/home/inbox/read/([0-9]+)',                UserInboxReadHandler,            name='user_inbox_read'),
            url('/user/home/team/create',                        UserTeamCreateHandler,           name='user_team_create'),
            url('/user/home/team/([0-9]+)',                      UserTeamHandler,                 name='user_team'),

            # API
            url('/api/judge/get_next_submission',                APIJudgeGetNextSubmissionHandler, name='api_judge_get_next_submission'),
            url('/api/judge/announce',                           APIJudgeAnnounceHandler,          name='api_judge_announce'),
            url('/api/judge/verdict',                            APIJudgeVerdictHandler,           name='api_judge_verdict'),

            # Admin
            url('/admin',                                        AdminHandler,                    name='admin'),
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
            login_url = '/user/login/',
        )

        tornado.web.Application.__init__(self, handlers, **settings)
        db_engine = create_engine(options.db_path, convert_unicode=True, echo=options.debug)
        models.Base.metadata.create_all(db_engine)
        # self.db = scoped_session(sessionmaker(bind=db_engine))
        self.db = sessionmaker(bind=db_engine)

        logger = logging.getLogger()
        if options.debug:
            logger.setLevel(logging.DEBUG)

        if options.local:
            test_data.add_test_data(self, self.db())

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
