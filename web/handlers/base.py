from tornado.web import RequestHandler
from models import User
import tornado.locale
from queries import Queries

class BaseHandler(RequestHandler):

    def get_user_locale(self):
        return tornado.locale.get('is_IS')

    def get_current_user(self):
        if self.cookies and 'user' in self.cookies:
            id = self.get_secure_cookie('user')
            try:
                return self.q.db.query(User).filter_by(id=id, active=True).one()
            except:
                self.clear_cookie('user')
        return None

    def get_template_namespace(self):
        namespace = RequestHandler.get_template_namespace(self)
        namespace.update(dict(q = self.q))

        return namespace

    def prepare(self):
        self.q = Queries(self)

    def on_finish(self):
        self.q.close()

