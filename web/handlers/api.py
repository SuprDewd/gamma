from base import BaseHandler
from tornado.web import authenticated
from ui_modules import PaginationModule
import datetime
import json
from models import Problem, Submission, ProgrammingLanguage, ContestProblem, JudgeQueue, Team, User

class AllProblemsHandler(BaseHandler):
    def get(self, cur_page=None):
        sess = self.db()
        problems = Problem.get_public(sess)
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

class APIHandler(BaseHandler):
    def get_current_user(self):
        username = self.get_argument('username')
        api_key = self.get_argument('api_key')

        try:
            return self.db().query(User).filter_by(username=username, api_key=api_key, active=True).first()
        except:
            return None

    def check_xsrf_cookie(self):
        pass

class APIJudgeAnnounceHandler(APIHandler):
    @authenticated
    def post(self):
        sess = self.db()
        contest_id = int(self.get_argument('contest_id'))

        if not self.current_user.can_judge_contest(sess, contest_id):
            self.write(json.dumps({'error': 'ACCESS_DENIED'}))
            return

        queue_item = JudgeQueue.get_by_submission_id(sess, int(self.get_argument('submission_id')))
        queue_item.last_announce = datetime.datetime.now()

        sess.commit()
        self.write(json.dumps({'announce_timeout': JudgeQueue.ANNOUNCE_TIMEOUT}))

class APIJudgeVerdictHandler(APIHandler):
    @authenticated
    def post(self):
        sess = self.db()
        contest_id = int(self.get_argument('contest_id'))

        if not self.current_user.can_judge_contest(sess, contest_id):
            self.write(json.dumps({'error': 'ACCESS_DENIED'}))
            return

        submission = Submission.get_by_id(sess, int(self.get_argument('submission_id')))
        submission.verdict = self.get_argument('verdict')

        queue_item = JudgeQueue.get_by_submission_id(sess, int(self.get_argument('submission_id')))
        sess.delete(queue_item)

        sess.commit()
        self.write(json.dumps({'announce_timeout': JudgeQueue.ANNOUNCE_TIMEOUT}))

class APIJudgeGetNextSubmissionHandler(APIHandler):
    @authenticated
    def post(self):
        sess = self.db()
        contest_id = int(self.get_argument('contest_id'))

        # TODO: Remove begin
        # import random
        # if random.randint(0,10) == 0:
        #     new_sub = Submission(team_id=1, problem_id=1, contest_id=contest_id, solution='', solution_lang_id=1)
        #     sess.add(new_sub)
        #     sess.flush()
        #     sess.add(JudgeQueue(submission_id=new_sub.id))
            # sess.commit()
        # TODO: Remove end

        if not self.current_user.can_judge_contest(sess, contest_id):
            self.write(json.dumps({'error': 'ACCESS_DENIED'}))
            return

        nxt = JudgeQueue.get_next(sess, contest_id=contest_id)

        if not nxt:
            self.write(json.dumps({'error': 'NO_SUBMISSIONS'}))
            return

        team = Team.get_by_id(sess, nxt.team_id)
        problem = Problem.get_by_id(sess, nxt.problem_id)
        contest_problem = ContestProblem.get_by_id(sess, contest_id=contest_id, problem_id=nxt.problem_id)
        solution_lang = ProgrammingLanguage.get_by_id(sess, nxt.solution_lang_id)

        res = {
            'submission': {
                'id': nxt.id
            },
            'team': {
                'name': team.name
            },
            'problem': {
                'name': problem.name,
                'short_id': contest_problem.short_id
            },
            'solution': {
                'code': nxt.solution,
                'lang': {
                    'name': solution_lang.name,
                    'compile_cmd': solution_lang.compile_cmd,
                    'run_cmd': solution_lang.run_cmd,
                }
            },
            'announce_timeout': JudgeQueue.ANNOUNCE_TIMEOUT,
            'time_limit': problem.time_limit,
            'memory_limit': problem.memory_limit,
            'tests': []
        }

        for t in problem.get_tests(sess).all():
            res['tests'].append({
                'input': t.input,
                'output': t.output,
            })

        if problem.checker:
            checker_lang = ProgrammingLanguage.get_by_id(sess, problem.checker_lang_id)
            res['checker'] = {
                'name': checker_lang.name,
                'compile_cmd': checker_lang.compile_cmd,
                'run_cmd': checker_lang.run_cmd,
            }

        self.write(json.dumps(res))


