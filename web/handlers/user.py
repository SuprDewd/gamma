from tornado.web import authenticated
from util import not_authenticated
from base import BaseHandler
from models import User, Team, TeamMember, Message
import util
import time


class UserLoginHandler(BaseHandler):
    @not_authenticated
    def get(self):
        self.render('user/login.html', incorrect_login=False)

    @not_authenticated
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        next = self.get_argument('next', '/') # TODO: use named routes
        user = self.q.User_login(username, password)

        if user:
            # XXX: is this safe?
            self.set_secure_cookie('user', str(user.id), expires_days=30)
            # XXX: make sure only redirecting internally
            self.redirect(next)
        else:
            self.render('user/login.html', incorrect_login=True)


class UserLogoutHandler(BaseHandler):
    @authenticated
    def get(self):
        self.clear_cookie('user')
        self.redirect('/') # TODO: use named routes


class UserRegisterHandler(BaseHandler):
    @not_authenticated
    def get(self):
        self.render('user/register.html', errs={},
                                     username=None,
                                     email=None,
                                     full_name=None,
                                     institute=None)

    @not_authenticated
    def post(self):
        username = self.get_argument('username')
        email = self.get_argument('email')
        full_name = self.get_argument('full_name')
        institute = self.get_argument('institute')
        password = self.get_argument('password')
        password_confirm = self.get_argument('password_confirm')

        errs = self.q.User_validate(
                username=username,
                email=email,
                name=full_name,
                institute=institute,
                password=password,
                password_confirm=password_confirm)

        if not errs:
            user = self.q.User_register(
                    username=username,
                    password=password,
                    email=email,
                    name=full_name,
                    institute=institute)

            # TODO: send email with confirmation key
            user.active = True
            self.q.db.commit()

            # TODO: pass on the email of the newly created user
            self.redirect('/user/register/successful/') # TODO: use named routes
        else:
            self.render('user/register.html',
                    errs=errs,
                    username=username,
                    email=email,
                    full_name=full_name,
                    institute=institute)


class UserRegisterSuccessfulHandler(BaseHandler):
    @not_authenticated
    def get(self):
        # TODO: pass on the email of the newly created user
        self.render('user/register_successful.html')


class UserRegisterConfirmHandler(BaseHandler):
    @not_authenticated
    def get(self, code):
        # TODO: handle confirmation code
        pass


class UserProfileHandler(BaseHandler):
    @authenticated
    def get(self):
        self.render('user/profile.html', current_page='profile')


class UserPasswordHandler(BaseHandler):
    @authenticated
    def get(self):
        self.render('user/password.html', current_page='password')


class UserInboxHandler(BaseHandler):
    @authenticated
    def get(self):
        self.render('user/inbox.html', current_page='inbox')


class UserInboxReadHandler(BaseHandler):
    @authenticated
    def get(self, message_id=None):
        message = self.q.get_or_404(Message, message_id)
        if self.q.User_get_messages(self.current_user).filter(Message.id == message.id).count() == 0: raise HTTPError(404)
        message.read = True
        self.q.db.commit()
        self.render('user/inbox_read.html', message=message, current_page='inbox')


class UserTeamCreateHandler(BaseHandler):
    @authenticated
    def get(self):
        self.render('user/team_create.html', errs={}, current_page='team_create')

    @authenticated
    def post(self):
        name = self.get_argument('name')
        errs = self.q.Team_validate(name=name)

        if not errs:
            team = self.q.Team_create(
                    name=name,
                    creator=self.current_user)

            self.redirect('/user/home/team/%d' % team.id) # TODO: use named routes
        else:
            self.render('user/team_create.html',
                    errs=errs,
                    name=name,
                    current_page='team_create')


class UserTeamHandler(BaseHandler):
    @authenticated
    def get(self, team_id=None):
        team = self.q.get_or_404(Team, team_id)
        if self.q.User_get_teams(self.current_user).filter(Team.id == team.id).count() == 0: raise HTTPError(404)
        self.render('user/team.html', current_page='team_%d' % team.id)

