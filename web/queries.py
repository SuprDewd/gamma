from models import *
import datetime
from sha import sha
from tornado.web import HTTPError
from sqlalchemy.orm.exc import NoResultFound

class Queries:

    def __init__(self, handler):
        self.handler = handler

    @property
    def db(self):
        if not hasattr(self, '_db'): setattr(self, '_db', self.handler.application.db())
        return self._db

    def close(self):
        if hasattr(self, '_db'):
            self._db.commit()
            self._db.close()

    # General
    def _cur_time(self, cur_time=None):
        return cur_time or datetime.datetime.now()

    def get_or_404(self, obj, id):
        try:
            n = int(id)
            return self.db.query(obj).filter_by(id=id).one()
        except (ValueError, NoResultFound):
            raise HTTPError(404)


    # User

    @staticmethod
    def _User_hash_password(username, password, salt):
        res = username + salt + password
        for i in range(15): res = sha(salt + res).hexdigest()
        return res

    def User_hash_password(self, username, password):
        return Queries._User_hash_password(username, password, self.handler.application.settings['cookie_secret'])

    def User_get_by_id(self, id):
        return self.db.query(User).filter_by(id=id).first()

    def User_get_main_team(self, user):
        return self.db.query(Team).filter_by(name=user.username).first()

    def User_get_teams(self, user, only_locked=False, only_led_by_me=False):
        res = self.db.query(Team) \
                  .join(TeamMember, Team.id == TeamMember.team_id) \
                  .filter(TeamMember.user_id == user.id)

        if only_locked: res = res.filter(Team.locked)
        if only_led_by_me: res = res.filter(TeamMember.leader)

        return res

    def User_get_messages(self, user, only_unread=False, only_read=False):
        res = self.db.query(Message) \
                  .filter_by(user_to_id=user.id)

        if only_unread: res = res.filter(not_(Message.read))
        if only_read: res = res.filter(Message.read)

        return res

    def User_validate(self, username, email, name, institute, password, password_confirm):
        _ = self.handler.locale.translate
        res = {}

        err = []
        if username:
            if len(username) < 3: err.append(_('Username too short'))
            if len(username) > 20: err.append(_('Username too long'))
            if not re.match(r'^[A-Za-z0-9_]*$', username): err.append(_('Invalid characters in username'))
            if not err and (self.db.query(User).filter_by(username=username).count() > 0
                            or self.db.query(Team).filter_by(name=username).count() > 0): err.append(_('Username is taken'))
        else: err.append(_('Field missing'))
        if err: res['username'] = err

        err = []
        if email:
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email) or len(email) > 300: err.append(_('Invalid email address'))
        else: err.append(_('Field missing'))
        if err: res['email'] = err

        err = []
        if password:
            if len(password) < 6: err.append(_("Password too short"))
            if len(password) > 30: err.append(_("Password too long"))
        else: err.append(_('Field missing'))
        if err: res['password'] = err

        err = []
        if password_confirm:
            if not 'password' in res and password_confirm != password: err.append(_("Passwords don't match"))
        else: err.append(_('Field missing'))
        if err: res['password_confirm'] = err

        return res

    def User_register(self, username, password, email, name, institute, create_main_team=True):
        try:
            user = User(username=username,
                        password_hash=self.User_hash_password(username, password),
                        email=email,
                        name=name,
                        institute=institute)

            self.db.add(user)
            self.db.flush()

            if create_main_team:
                team = self.Team_create(name=username, locked=True, creator=user)

            return user
        except:
            self.db.rollback()
            raise

    def User_login(self, username, password):
        return self.db.query(User).filter_by(
                username=username,
                password_hash=self.User_hash_password(username, password),
                active=True
            ).first()

    def User_has_permission(self, user, permission):
        # TODO: Implement permissions
        return True

    def User_can_judge_all_contests(self, user):
        return self.User_has_permission(user, 'CAN_JUDGE_ALL_CONTESTS')

    def can_judge_contest(self, user, contest_id):
        return self.User_has_permission(user, 'CAN_JUDGE_CONTEST_%d' % contest_id) or self.can_judge_all_contests()


    # Team
    def Team_add_member(self, team, user, leader=False):
        member = TeamMember(user_id=user.id, team_id=team.id, leader=leader)
        self.db.add(member)
        self.db.flush()
        return member

    def Team_get_by_id(self, id):
        return self.db.query(Team).filter_by(id=id).first()

    def Team_get_members(self, team):
        return self.db.query(TeamMember).filter_by(team_id=team.id)

    def Team_validate(self, name):
        _ = self.handler.locale.translate
        res = {}

        err = []
        if name:
            if len(name) < 3: err.append(_('Team name too short'))
            if len(name) > 20: err.append(_('Team name too long'))
            if not re.match(r'^[A-Za-z0-9_]*$', name): err.append(_('Invalid characters in team name'))
            if not err and (self.db.query(User).filter_by(username=name).count() > 0
                            or self.db.query(Team).filter_by(name=name).count() > 0): err.append(_('Team name is taken'))
        else: err.append(_('Field missing'))
        if err: res['name'] = err

        return res

    def Team_create(self, name, creator=None, locked=False):
        try:
            team = Team(name=name, locked=locked)

            self.db.add(team)
            self.db.flush()

            if creator:
                member = self.Team_add_member(team=team, user=creator, leader=True)

            return team
        except:
            self.db.rollback()
            raise


    # TeamMember
    def TeamMember_get_team(self, team_member):
        return self.Team_get_by_id(team_member.team_id)

    def TeamMember_get_user(self, team_member):
        return self.User_get_by_id(team_member.user_id)


    # TeamInvitation


    # Contest
    def Contest_get_by_id(self, contest_id, only_open_for_me=False):
        contest = self.db.query(Contest).filter_by(id=contest_id).first()
        if not contest: return None
        ok = False
        if only_open_for_me:
            if contest.public:
                if contest.open_for_guests:
                    ok = True
                elif self.handler.current_user and self.Contest_is_registered(contest, self.handler.current_user):
                    ok = True
        return contest if ok else None

    def Contest_get_submissions(self, contest_id, team_id=None):
        res = self.db.query(Submission).filter_by(contest_id=contest_id)
        if team_id is not None: res = res.filter_by(team_id=team_id)
        return res

    def Contest_after_start(self, contest, cur_time=None):
        return contest.start_time <= self._cur_time(cur_time)

    def Contest_after_end(self, contest, cur_time=None):
        return contest.duration != None and contest.start_time + datetime.timedelta(0, 60*contest.duration) < self._cur_time(cur_time)

    def Contest_is_running(self, contest, cur_time):
        cur_time = self._cur_time(cur_time)
        return self.Contest_after_start(contest, cur_time) and not self.Contest_after_end(contest, cur_time)

    def Contest_after_registration_start(self, contest, cur_time=None):
        return contest.registration_start and contest.registration_start < self._cur_time(cur_time)

    def Contest_after_registration_end(self, contest, cur_time=None):
        return contest.registration_end and contest.registration_end < self._cur_time(cur_time)

    def Contest_is_registration_open(self, contest, cur_time=None):
        cur_time = self._cur_time(cur_time)
        return self.Contest_after_registration_start(contest, cur_time) and not self.Contest_after_registration_end(contest, cur_time)

    def Contest_get_user_team(self, contest, user):
        return self.db.query(Registration) \
                 .join(Team, Registration.team_id == Team.id) \
                 .join(TeamMember, Team.id == TeamMember.team_id) \
                 .filter(Registration.contest_id == contest.id) \
                 .filter(TeamMember.user_id == user.id) \
                 .first()

    def Contest_is_registered(self, contest, user):
        return self.Contest_get_user_team(contest, user) is not None

    def Contest_registration_count(self, contest):
        return self.db.query(Registration) \
                 .filter_by(contest_id=contest.id) \
                 .count()

    def Contest_elapsed(self, contest, cur_time=None):
        return (self._cur_time(cur_time) - contest.start_time).total_seconds() / 60 if contest.start_time else None

    def Contest_get_problems(self, contest, only_open=False, also_after_close=False, cur_time=None):
        res = self.db.query(ContestProblem) \
                .filter_by(contest_id=contest.id)

        if only_open and contest.start_time:
            at = self.Contest_elapsed(contest, self._cur_time(cur_time))
            res = res.filter(or_(ContestProblem.start_time == None, ContestProblem.start_time <= at))

            if not also_after_close:
                res = res.filter(or_(ContestProblem.end_time == None, at <= ContestProblem.end_time))

        res = res.order_by(ContestProblem.short_id)
        return res

    def Contest_get_problem(self, contest, short_id):
        return self.db.query(ContestProblem) \
                 .filter_by(contest_id=contest.id, short_id=short_id) \
                 .first()

    def Contest_get_public(self):
        return self.db.query(Contest) \
                .filter(Contest.public)

    # @staticmethod
    # def get_current(db, cur_time=None):
    #     cur_time = cur_time or datetime.datetime.now()
    #     return db.query(Contest).filter(and_(Contest.start_time != None, Contest.start_time <= cur_time, or_(Contest.end_time == None, cur_time <= Contest.start_time + datetime.timedelta(0, 60 * Contest.duration))))

    # @staticmethod
    # def get_past(db, cur_time=None, rng=None):
    #     cur_time = cur_time or datetime.datetime.now()
    #     res = db.query(Contest).filter(and_(Contest.start_time != None, cur_time > Contest.start_time + datetime.timedelta(0, 60 * Contest.duration)))
    #     if rng: return res[rng[0]:rng[1]]
    #     return rng.all()

    # @staticmethod
    # def get_upcoming(db, cur_time=None):
    #     cur_time = cur_time or datetime.datetime.now()
    #     return db.query(Contest).filter(and_(Contest.start_time != None, cur_time < Contest.start_time))

    def Contest_get_standings(self, contest, cur_time=None):
        cur_time = self._cur_time(cur_time)
        standings = {}

        for submission in self.db.query(Submission).filter_by(contest_id=contest.id).filter(Submission.verdict.in_(['AC', 'WA', 'TLE', 'PE', 'RE', 'MLE'])).order_by(Submission.submitted):
            short_id = self.db.query(ContestProblem).filter_by(contest_id=contest.id, problem_id=submission.problem_id).one().short_id
            # standings.setdefault(submission.team_id, [0, 0, {}])
            standings.setdefault(submission.team_id, {})
            standings[submission.team_id].setdefault(short_id, [0, None])
            if standings[submission.team_id][short_id][1] is not None: continue
            if submission.verdict == 'AC':
                # standings[submission.team_id][0] += 1
                # standings[submission.team_id][1] += submission.submitted
                standings[submission.team_id][short_id][1] = (submission.submitted - contest.start_time).total_seconds() / 60.0
            else:
                # standings[submission.team_id][1] += 20
                standings[submission.team_id][short_id][0] += 1

        standings = [
            (
                self.Team_get_by_id(team_id),
                sum( 1 if ac_time else 0 for _, [_, ac_time] in problems.items() ),
                sum( 20*incorrect_tries + ac_time if ac_time else 0 for _, [incorrect_tries, ac_time] in problems.items() ) if contest.start_time else 0,
                [
                    (short_id, incorrect_tries, ac_time)
                    for short_id, [incorrect_tries, ac_time] in sorted(problems.items())
                ]
            ) for team_id, problems in standings.items()
        ]

        def comparer(a, b):
            if a[1] != b[1]: return -cmp(a[1], b[1])
            if a[2] != b[2]: return cmp(a[2], b[2])
            return 0

        standings.sort(comparer)
        return standings

        # standings = []
        # for team in self.teams:
        #     points = 0
        #     penalty = 0
        #     summary = []
        #     for problem in self.problems:
        #         first_ac = db.query(ContestSubmission).filter_by(team_id=team.team_id, contest_id=self.id, problem_id=problem.problem_id, verdict='AC').order_by(ContestSubmission.submitted).first()
        #         count = db.query(ContestSubmission).filter_by(team_id=team.team_id, contest_id=self.id, problem_id=problem.problem_id).filter(ContestSubmission.verdict.in_(['WA', 'TLE', 'PE', 'RE', 'MLE']))
        #         if first_ac: count = count.filter(ContestSubmission.submitted <= first_ac.submitted)
        #         count = count.count()
        #         if first_ac:
        #             points += 1
        #             penalty += 20 * count
        #         summary.append((first_ac.submitted if first_ac else None, count))
        #     standings.append({'points': points, 'penalty': penalty, 'team': team.team, 'problems': summary})

        # def comparer(a, b):
        #     if a['points'] != b['points']: return -cmp(a['points'], b['points'])
        #     if a['penalty'] != b['penalty']: return cmp(a['penalty'], b['penalty'])
        #     return 0
        # standings.sort(comparer)
        # return standings


    # Registration

    # ProgrammingLanguage

    def ProgrammingLanguage_get_all(self):
        return self.db.query(ProgrammingLanguage)

    def ProgrammingLanguage_get_by_id(self, id):
        return self.db.query(ProgrammingLanguage) \
                 .filter_by(id=id) \
                 .first()


    # Problem
    def Problem_get_by_id(self, id):
        return self.db.query(Problem).filter_by(id=id).first()

    def Problem_users_solved_count(self, problem):
        return self.db.query(Submission.team_id) \
                 .filter_by(problem_id=problem.id, contest_id=None, verdict='AC') \
                 .distinct() \
                 .count()

    def Problem_users_tried_count(self, problem):
        return self.db.query(Submission.team_id) \
                 .filter_by(problem_id=problem.id, contest_id=None) \
                 .distinct() \
                 .count()

    def Problem_get_tests(self, problem, db):
        return self.db.query(Test) \
                 .filter_by(problem_id=problem.id)

    def Problem_get_public(self):
        return self.db.query(Problem).filter(Problem.public)


    # Test

    # Submission
    def Submission_get_by_id(self, id):
        return self.db.query(Submission) \
                 .filter_by(id=id) \
                 .first()

    def Submission_submit(self, team_id, problem_id, contest_id, solution, solution_lang_id):
        try:
            submission = Submission(team_id=team_id,
                        problem_id=problem_id,
                        contest_id=contest_id,
                        solution=solution,
                        solution_lang_id=solution_lang_id,
                        verdict='Pending')

            self.db.add(submission)
            self.db.flush()

            return submission
        except:
            self.db.rollback()
            raise


    # JudgeQueue
    def JudgeQueue_get_next(self, contest_id=None, any_contest=False):
        # TODO: Make sure each client gets a different submission

        try:
            res = db.query(JudgeQueue).with_lockmode('update') \
                    .join(Submission, JudgeQueue.submission_id == Submission.id) \
                    .filter(or_(JudgeQueue.last_announce == None, JudgeQueue.last_announce <= datetime.datetime.now() - datetime.timedelta(0, JudgeQueue.REAL_ANNOUNCE_TIMEOUT / 1000.0, 0)))

            if not any_contest: res = res.filter(Submission.contest_id == contest_id)
            nxt = res.first()
            if not nxt: return None

            nxt.last_announce = datetime.datetime.now()
            trans.commit()

            return db.query(Submission) \
                     .filter_by(id=nxt.submission_id) \
                     .one()
        except:
            trans.rollback()
            raise

        # trans = db.begin(subtransactions=True)
        # try:
        #     res = db.query(JudgeQueue) \
        #             .join(Submission, JudgeQueue.submission_id == Submission.id) \
        #             .filter(or_(JudgeQueue.last_announce == None, JudgeQueue.last_announce <= datetime.datetime.now() - datetime.timedelta(0, JudgeQueue.REAL_ANNOUNCE_TIMEOUT / 1000.0, 0)))

        #     if not any_contest: res = res.filter(Submission.contest_id == contest_id)
        #     nxt = res.first()
        #     if not nxt: return None

        #     nxt.last_announce = datetime.datetime.now()
        #     trans.commit()

        #     return db.query(Submission) \
        #              .filter_by(id=nxt.submission_id) \
        #              .one()
        # except:
        #     trans.rollback()
        #     raise

    def JudgeQueue_get_by_submission_id(self, submission_id):
        return self.db.query(JudgeQueue) \
                 .filter_by(submission_id=submission_id) \
                 .first()

    # ContestProblem
    def ContestProblem_get_by_id(self, problem_id, contest_id):
        return self.db.query(ContestProblem) \
                 .filter_by(problem_id=problem_id, contest_id=contest_id) \
                 .first()

    def ContestProblem_get_problem(self, contest_problem):
        return self.db.query(Problem) \
                 .filter_by(id=contest_problem.problem_id) \
                 .first()

    def ContestProblem_is_open(self, contest_problem, elapsed):
        return (not contest_problem.start_time or elapsed >= contest_problem.start_time) and (not contest_problem.end_time or contest_problem.end_time <= elapsed)

    def ContestProblem_teams_solved_count(self, contest_problem):
        return self.db.query(Submission.team_id).filter_by(contest_id=contest_problem.contest_id, problem_id=contest_problem.problem_id, verdict='AC').distinct().count()

    def ContestProblem_teams_tried_count(self, contest_problem):
        return self.db.query(Submission.team_id).filter_by(contest_id=contest_problem.contest_id, problem_id=contest_problem.problem_id).distinct().count()

    # ProblemComment

    # ProblemCommentLike

    # Message
    def Message_get_user_to(self, message):
        return self.db.query(User).filter_by(id=message.user_to_id).first()

    def Message_get_user_from(self, message):
        return self.db.query(User).filter_by(id=message.user_from_id).first()

    # Permission

    # PermissionGroup

    # PermissionGroupUser

