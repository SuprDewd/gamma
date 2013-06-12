from tornado.web import authenticated
from util import not_authenticated
from base import BaseHandler
from models import User, Team, TeamMember
import util
import time


class LoginHandler(BaseHandler):
    @not_authenticated
    def get(self):
        self.render('auth/login.html', incorrect_login=False)

    @not_authenticated
    def post(self):
        sess = self.db()

        username = self.get_argument('username')
        password = self.get_argument('password')
        next = self.get_argument('next', '/') # TODO: use named routes
        user = User.login(sess, username, password, self.application.settings['cookie_secret'])

        if user:
            # XXX: is this safe?
            self.set_secure_cookie('user', str(user.id), expires_days=30)
            # XXX: make sure only redirecting internally
            self.redirect(next)
        else:
            self.render('auth/login.html', incorrect_login=True)


class LogoutHandler(BaseHandler):
    @authenticated
    def get(self):
        self.clear_cookie('user')
        self.redirect('/') # TODO: use named routes


class RegisterHandler(BaseHandler):
    @not_authenticated
    def get(self):
        self.render('auth/register.html', errs={},
                                     username=None,
                                     email=None,
                                     full_name=None,
                                     institute=None)

    @not_authenticated
    def post(self):
        sess = self.db()

        username = self.get_argument('username')
        email = self.get_argument('email')
        full_name = self.get_argument('full_name')
        institute = self.get_argument('institute')
        password = self.get_argument('password')
        password_confirm = self.get_argument('password_confirm')

        errs = User.validate(sess, self.locale,
                username=username,
                email=email,
                name=full_name,
                institute=institute,
                password=password,
                password_confirm=password_confirm)

        if not errs:
            user = User.register(
                    db=sess,
                    username=username,
                    password=password,
                    email=email,
                    name=full_name,
                    institute=institute)

            # TODO: send email with confirmation key
            user.active = True
            sess.commit()

            # TODO: pass on the email of the newly created user
            self.redirect('/user/register/successful/') # TODO: use named routes
        else:
            self.render('auth/register.html',
                    errs=errs,
                    username=username,
                    email=email,
                    full_name=full_name,
                    institute=institute)


class RegisterSuccessfulHandler(BaseHandler):
    def get(self):
        # TODO: pass on the email of the newly created user
        self.render('auth/register_successful.html')


class RegisterConfirmHandler(BaseHandler):
    def get(self, code):
        # TODO: handle confirmation code
        pass

