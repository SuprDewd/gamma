from base import BaseHandler
from ui_modules import PaginationModule
import datetime
import util
from models import *
from tornado.web import authenticated

# TODO: make sure contest is open (has started and not ended)

class ContestBaseHandler(BaseHandler):
    def get_cur_contest(self, contest_id):
        try:
            contest = self.q.Contest_get_by_id(int(contest_id), only_open_for_me=True)
            if not contest: raise HTTPError(404)
            return contest
        except ValueError:
            raise HTTPError(404)

class AllContestsHandler(BaseHandler):
    def get(self, cur_page=None):
        upcoming_contests = []
        current_contests = []
        past_contests = []

        for c in self.q.Contest_get_public().all():
            if self.q.Contest_after_end(c):
                past_contests.append(c)
            elif self.q.Contest_after_start(c):
                current_contests.append(c)
            else:
                upcoming_contests.append(c)

        cur_page = int(cur_page) if cur_page else 0
        items_per_page = 10 # TODO: extract to config
        page_location = '/contests/%d/' # TODO: use named routes somehow
        past_contests = list(reversed(past_contests))
        return self.render('contest/all.html',
                    cur_page=cur_page,
                    item_count=len(past_contests),
                    items_per_page=items_per_page,
                    page_location=page_location,
                    past_contests=PaginationModule.current_items(past_contests, cur_page, items_per_page),
                    upcoming_contests=upcoming_contests,
                    current_contests=current_contests)

class ContestRegisterHandler(ContestBaseHandler):
    @authenticated
    def get(self, contest_id=None):
        contest = self.q.get_or_404(Contest, contest_id)
        if not contest.public: raise HTTPError(404)
        # TODO: make sure contest is open for registration
        if self.q.Contest_is_registered(contest, self.current_user):
            self.render('contest/register.html', already_registered=True, contest=contest)
        else:
            self.render('contest/register.html',
                    already_registered=False,
                    contest=contest,
                    teams=self.User_get_teams(self.current_user, only_locked=True))

    @authenticated
    def post(self, contest_id=None):
        contest = self.q.get_or_404(Contest, contest_id)
        if not contest.public: raise HTTPError(404)
        team_id = int(self.get_argument('team_id'))
        # TODO: make sure contest is open for registration
        if not self.q.Contest_is_registered(contest, self.current_user) and self.q.db.query(TeamMember).filter_by(team_id=team_id, user_id=self.current_user.id).count() > 0 and self.q.db.query(Team).filter_by(id=team_id, locked=True).count() > 0 and (contest.max_team_size == None or self.q.db.query(TeamMember).filter_by(team_id=team_id).count() <= contest.max_team_size):
            self.q.db.add(Registration(team_id=team_id, contest_id=contest.id))
            self.q.db.commit()
        else:
            # TODO: display error?
            pass

        self.redirect('/contests/')

class ContestRegisteredHandler(ContestBaseHandler):
    def get(self, contest_id=None):
        contest = self.q.get_or_404(Contest, contest_id)
        if not contest.public: raise HTTPError(404)
        self.render('contest/registered.html',
                contest=contest,
                registered=self.q.db.query(Team).join(Registration, Team.id == Registration.team_id).filter(Registration.contest_id == contest.id).all())

class ContestHandler(ContestBaseHandler):
    def get(self, contest_id=None):
        contest = self.get_cur_contest(contest_id)
        problems = self.q.Contest_get_problems(contest, only_open=True)
        if problems:
            self.redirect('/contest/%d/problem/%s' % (contest.id, problems[0].short_id))
        else:
            self.redirect('/contest/%d/standings' % contest.id)

class ContestStandingsHandler(ContestBaseHandler):
    def get(self, contest_id=None):
        contest = self.get_cur_contest(contest_id)
        self.render('contest/standings.html', contest=contest, standings=self.q.Contest_get_standings(contest))

class ContestSubmissionsHandler(ContestBaseHandler):
    def get(self, contest_id=None, team_id=None):
        contest = self.get_cur_contest(contest_id)
        if team_id:
            try:
                team_id = int(team_id[1:])
            except:
                team_id = None

        submissions = self.q.Contest_get_submissions(contest.id, team_id=team_id).order_by('Submission.submitted').all()[::-1]
        self.render('contest/submissions.html', contest=contest, submissions=submissions)

class ContestProblemHandler(ContestBaseHandler):
    def get(self, contest_id=None, short_id=None):
        contest = self.get_cur_contest(contest_id)

        try:
            problem = self.q.Contest_get_problem(contest, short_id)
        except NoResultFound:
            raise HTTPError(404)

        if not self.q.ContestProblem_is_open(problem, self.q.Contest_elapsed(contest)):
            raise HTTPError(404)

        self.render('contest/problem.html', contest=contest, problem=problem)

    def post(self, contest_id=None, short_id=None):
        contest = self.get_cur_contest(contest_id)
        team_id = self.q.Contest_get_user_team(contest, self.current_user).team_id

        try:
            problem = self.q.Contest_get_problem(contest, short_id)
        except NoResultFound:
            raise HTTPError(404)

        if not self.q.ContestProblem_is_open(problem, self.q.Contest_elapsed(contest)):
            raise HTTPError(404)

        if 'source_file' in self.request.files:
            source_code = self.request.files['source_file']['body']
        else:
            source_code = self.get_argument('source_code')

        prog_lang_id = self.get_argument('prog_lang')

        self.q.Submission_submit(team_id=team_id,
                    problem_id=problem.problem_id,
                    contest_id=contest.id,
                    solution=source_code,
                    solution_lang_id=prog_lang_id)

        self.redirect(self.reverse_url('contest_team_submissions', contest.id, team_id))

