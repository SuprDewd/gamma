from base import BaseHandler
from ui_modules import PaginationModule
import datetime
from models import Problem, Submission

class ProblemViewModel:
    def __init__(self, id, name, correct_submissions, total_submissions):
        self.id = id
        self.name = name
        self.correct_submissions = correct_submissions
        self.total_submissions = total_submissions

class AllProblemsHandler(BaseHandler):
    def get(self, cur_page=None):
        sess = self.db()
        problems = [ ProblemViewModel(p.id, p.name,
                                      p.correct_submission_count(sess),
                                      p.total_submission_count(sess))
                     for p in Problem.get_public(sess) ]

        cur_page = int(cur_page) if cur_page else 0
        items_per_page = 10 # TODO: extract to config
        page_location = '/problems/%d/' # TODO: use named routes somehow
        return self.render('problem/all.html',
                    cur_page=cur_page,
                    item_count=len(problems),
                    items_per_page=items_per_page,
                    page_location=page_location,
                    problems=PaginationModule.current_items(problems, cur_page, items_per_page))
