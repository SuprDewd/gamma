from base import BaseHandler
from ui_modules import PaginationModule
import datetime
import util
from models import *
from tornado.web import authenticated

class AllContestsHandler(BaseHandler):
    def get(self, cur_page=None):
        sess = self.db()

        upcoming_contests = []
        current_contests = []
        past_contests = []

        for c in Contest.get_public(sess):
            if c.after_end():
                past_contests.append(c)
            elif c.after_start():
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

class ContestRegisterHandler(BaseHandler):
    @authenticated
    def get(self, contest_id=None):
        sess = self.db
        contest = util.get_or_404(sess, Contest, contest_id)
        if not contest.public: raise HTTPError(404)
        if contest.is_registered(sess, self.current_user):
            self.render('contest/register.html', already_registered=True, contest=contest)
        else:
            self.render('contest/register.html',
                    already_registered=False,
                    contest=contest,
                    teams=sess.query(Team).join(TeamMember, Team.id == TeamMember.team_id).filter(TeamMember.user_id == self.current_user.id, Team.locked))

    @authenticated
    def post(self, contest_id=None):
        sess = self.db
        contest = util.get_or_404(sess, Contest, contest_id)
        if not contest.public: raise HTTPError(404)
        team_id = int(self.get_argument('team_id'))
        if not contest.is_registered(sess, self.current_user) and sess.query(TeamMember).filter_by(team_id=team_id, user_id=self.current_user.id).count() > 0 and sess.query(Team).filter_by(id=team_id, locked=True).count() > 0 and (contest.max_team_size == None or sess.query(TeamMember).filter_by(team_id=team_id).count() <= contest.max_team_size):
            sess.add(Registration(team_id=team_id, contest_id=contest.id))
            sess.commit()
        else:
            # TODO: display error?
            pass

        self.redirect('/contests/')

class ContestRegisteredHandler(BaseHandler):
    def get(self, contest_id=None):
        sess = self.db
        contest = util.get_or_404(sess, Contest, contest_id)
        if not contest.public: raise HTTPError(404)
        self.render('contest/registered.html',
                contest=contest,
                registered=sess.query(Team).join(Registration, Team.id == Registration.team_id).filter(Registration.contest_id == contest.id).all())

class ContestHandler(BaseHandler):
    def get(self, contest_id=None):
        sess = self.db
        contest = util.get_or_404(sess, Contest, contest_id)
        if not contest.public or (not contest.open_for_guests and (not self.current_user or not self.is_registered(sess, self.current_user))): raise HTTPError(404)
        self.render('contest/problems.html', contest=contest, problems=sess.query(Problem).join(ContestProblem, Problem.id == ContestProblem.problem_id).filter(ContestProblem.contest_id == contest_id).all())

class ContestStandingsHandler(BaseHandler):
    def get(self, contest_id=None):
        sess = self.db
        contest = util.get_or_404(sess, Contest, contest_id)
        if not contest.public: raise HTTPError(404)
        self.render('contest/standings.html', contest=contest)

