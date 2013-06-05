from base import BaseHandler
from pagination import PaginationModule
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
        problems = []
        for p in self.application.db.query(Problem).filter(Problem.public).all():
            correct_submissions = self.application.db.query(Submission).filter_by(problem_id=p.id, verdict='AC').count()
            total_submissions = self.application.db.query(Submission).filter_by(problem_id=p.id).count()
            problems.append(ProblemViewModel(p.id, p.name, correct_submissions, total_submissions))
        cur_page = int(cur_page) if cur_page else 0
        items_per_page = 10
        page_location = '/problems/%d/'

        return self.render('all_problems.html',
                    cur_page=cur_page,
                    item_count=len(problems),
                    items_per_page=items_per_page,
                    page_location=page_location,
                    problems=PaginationModule.current_items(problems, cur_page, items_per_page))
