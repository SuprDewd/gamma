from tornado.web import RequestHandler
from models import User
import tornado.locale

class BaseHandler(RequestHandler):
    def get_user_locale(self):
        return tornado.locale.get('is_IS')

    def get_current_user(self):
        if self.cookies and 'user' in self.cookies:
            id = self.get_secure_cookie('user')
            try:
                return self.db().query(User).filter_by(id=id, active=True).one()
            except:
                self.clear_cookie('user')
        return None

    @property
    def db(self):
        return self.application.db
