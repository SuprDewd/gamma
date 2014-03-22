from tornado.web import HTTPError
import functools
from uuid import uuid4

def not_authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.current_user:
            if self.request.method in ("GET", "HEAD"):
                self.redirect('/') # TODO: use named routes
                return
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper

def generate_confirm_token():
    return uuid4().hex
