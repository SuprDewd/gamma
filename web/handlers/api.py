from base import BaseHandler
from tornado.web import authenticated
from ui_modules import PaginationModule
import datetime
import json
from models import Problem, Submission, ProgrammingLanguage, ContestProblem, JudgeQueue, Team, User

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
        contest_id = int(self.get_argument('contest_id'))

        if not self.q.User_can_judge_contest(self.current_user, contest_id):
            self.write(json.dumps({'error': 'ACCESS_DENIED'}))
            return

        queue_item = self.q.JudgeQueue_get_by_submission_id(int(self.get_argument('submission_id')))
        queue_item.last_announce = datetime.datetime.now()

        self.q.db.commit()
        self.write(json.dumps({'announce_timeout': JudgeQueue.ANNOUNCE_TIMEOUT}))

class APIJudgeVerdictHandler(APIHandler):
    @authenticated
    def post(self):
        contest_id = int(self.get_argument('contest_id'))

        if not self.q.JudgeQueue_can_judge_contest(self.current_user, contest_id):
            self.write(json.dumps({'error': 'ACCESS_DENIED'}))
            return

        submission = self.q.Submission_get_by_id(int(self.get_argument('submission_id')))
        submission.verdict = self.get_argument('verdict')

        queue_item = self.q.JudgeQueue_get_by_submission_id(int(self.get_argument('submission_id')))
        self.q.db.delete(queue_item)

        self.q.db.commit()
        self.write(json.dumps({'announce_timeout': JudgeQueue.ANNOUNCE_TIMEOUT}))

class APIJudgeGetNextSubmissionHandler(APIHandler):
    @authenticated
    def post(self):
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

        if not self.q.User_can_judge_contest(self.current_user, contest_id):
            self.write(json.dumps({'error': 'ACCESS_DENIED'}))
            return

        nxt = self.q.JudgeQueue_get_next(contest_id=contest_id)

        if not nxt:
            self.write(json.dumps({'error': 'NO_SUBMISSIONS'}))
            return

        team = self.q.Team_get_by_id(nxt.team_id)
        problem = self.q.Problem_get_by_id(nxt.problem_id)
        contest_problem = self.q.ContestProblem_get_by_id(contest_id=contest_id, problem_id=nxt.problem_id)
        solution_lang = self.q.ProgrammingLanguage.get_by_id(nxt.solution_lang_id)

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

        for t in self.q.Problem_get_tests(problem).all():
            res['tests'].append({
                'input': t.input,
                'output': t.output,
            })

        if problem.checker:
            checker_lang = self.q.ProgrammingLanguage_get_by_id(problem.checker_lang_id)
            res['checker'] = {
                'name': checker_lang.name,
                'compile_cmd': checker_lang.compile_cmd,
                'run_cmd': checker_lang.run_cmd,
            }

        self.write(json.dumps(res))


