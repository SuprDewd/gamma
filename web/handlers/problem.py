from base import BaseHandler

class ProblemHandler(BaseHandler):
    def get(self, problem_id):
        self.write(problem_id)
