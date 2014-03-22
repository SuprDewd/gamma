from base import BaseHandler
from ui_modules import PaginationModule
import datetime
from models import Problem, Submission

class AllProblemsHandler(BaseHandler):
    def get(self, cur_page=None):
        problems = self.q.Problem_get_public().all()
        cur_page = int(cur_page) if cur_page else 0
        items_per_page = 10 # TODO: extract to config
        page_location = '/problems/%d/' # TODO: use named routes somehow
        return self.render('problem/all.html',
                    cur_page=cur_page,
                    item_count=len(problems),
                    items_per_page=items_per_page,
                    page_location=page_location,
                    problems=PaginationModule.current_items(problems, cur_page, items_per_page))

class ProblemHandler(BaseHandler):
    def get(self, problem_id):
        pass

