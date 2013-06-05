from tornado.web import HTTPError
from sha import sha
from uuid import uuid4
import functools

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

def hash_password(username, password, salt):
    res = username + salt + password
    for i in range(15): res = sha(salt + res).hexdigest()
    return res

