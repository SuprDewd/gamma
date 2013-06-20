from sqlalchemy import Column, Integer, Float, String, Text, DateTime, Boolean, ForeignKey, Enum, or_, and_, not_
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base, declared_attr
import datetime
import util
import re


Base = declarative_base()


class DefaultTable(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__


class User(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    username = Column(String(30), nullable=False, unique=True)
    password_hash = Column(String)
    email = Column(String(200))
    name = Column(String)
    institute = Column(String)
    api_key = Column(String)
    registered = Column(DateTime, default=datetime.datetime.now)
    active = Column(Boolean, default=False)
    confirm_token = Column(String, default=util.generate_confirm_token, unique=True)
    # teams = relationship('TeamMember')
    # main_team_id = Column(Integer, ForeignKey('Team.id'))

    def get_by_id(self, db, id):
        return db.query(User) \
                 .filter_by(id=id) \
                 .first()

    def get_main_team(self, db):
        return db.query(Team) \
                 .filter_by(name=self.username) \
                 .first()

    def get_teams(self, db, only_locked=False, only_led_by_me=False):
        res = db.query(Team) \
                .join(TeamMember, Team.id == TeamMember.team_id) \
                .filter(TeamMember.user_id == self.id)

        if only_locked: res = res.filter(Team.locked)
        if only_led_by_me: res = res.filter(TeamMember.leader)

        return res

    def get_messages(self, db, only_unread=False, only_read=False):
        res = db.query(Message) \
                .filter_by(user_to_id=self.id)

        if only_unread: res = res.filter(not_(Message.read))
        if only_read: res = res.filter(Message.read)

        return res

    @staticmethod
    def validate(db, locale, username, email, name, institute, password, password_confirm):
        _ = locale.translate
        res = {}

        err = []
        if username:
            if len(username) < 3: err.append(_('Username too short'))
            if len(username) > 20: err.append(_('Username too long'))
            if not re.match(r'^[A-Za-z0-9_]*$', username): err.append(_('Invalid characters in username'))
            if not err and (db.query(User).filter_by(username=username).count() > 0
                            or db.query(Team).filter_by(name=username).count() > 0): err.append(_('Username is taken'))
        else: err.append(_('Field missing'))
        if err: res['username'] = err

        err = []
        if email:
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email): err.append(_('Invalid email address'))
        else: err.append(_('Field missing'))
        if err: res['email'] = err

        err = []
        if password:
            if len(password) < 6: err.append(_("Password too short"))
        else: err.append(_('Field missing'))
        if err: res['password'] = err

        err = []
        if password_confirm:
            if not 'password' in res and password_confirm != password: err.append(_("Passwords don't match"))
        else: err.append(_('Field missing'))
        if err: res['password_confirm'] = err

        return res

    @staticmethod
    def register(db, username, password, salt, email, name, institute, create_main_team=True):
        try:
            user = User(username=username,
                        password_hash=util.hash_password(username, password, salt),
                        email=email,
                        name=name,
                        institute=institute)

            db.add(user)
            db.flush()

            if create_main_team:
                team = Team.create(db, name=username, locked=True, creator=user)

                # team = Team(name=username, locked=True)
                # db.add(team)
                # db.flush()
                # team_member = TeamMember(user_id=user.id, team_id=team.id, leader=True)
                # db.add(team_member)

            return user
        except:
            db.rollback()
            raise

    @staticmethod
    def login(db, username, password, salt):
        return db.query(User).filter_by(
                username=username,
                password_hash=util.hash_password(username, password, salt),
                active=True
            ).first()

    def has_permission(self, db, permission):
        # TODO: Implement permissions
        return True

    def can_judge_all_contests(self, sess):
        return self.has_permission(sess, 'CAN_JUDGE_ALL_CONTESTS')

    def can_judge_contest(self, sess, contest_id):
        return self.has_permission(sess, 'CAN_JUDGE_CONTEST_%d' % contest_id) or self.can_judge_all_contests(sess)


class Team(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    locked = Column(Boolean, nullable=False, default=False)
    # members = relationship('TeamMember')
    # contests = relationship('Registration')

    def add_member(self, db, user, leader=False):
        member = TeamMember(user_id=user.id, team_id=self.id, leader=leader)
        db.add(member)
        db.flush()
        return member

    @staticmethod
    def get_by_id(db, id):
        return db.query(Team).filter_by(id=id).first()

    @staticmethod
    def validate(db, locale, name):
        _ = locale.translate
        res = {}

        err = []
        if name:
            if len(name) < 3: err.append(_('Team name too short'))
            if len(name) > 20: err.append(_('Team name too long'))
            if not re.match(r'^[A-Za-z0-9_]*$', name): err.append(_('Invalid characters in team name'))
            if not err and (db.query(User).filter_by(username=name).count() > 0
                            or db.query(Team).filter_by(name=name).count() > 0): err.append(_('Team name is taken'))
        else: err.append(_('Field missing'))
        if err: res['name'] = err

        return res

    @staticmethod
    def create(db, name, creator=None, locked=False):
        try:
            team = Team(name=name, locked=locked)

            db.add(team)
            db.flush()

            if creator:
                member = team.add_member(db, user=creator, leader=True)

            return team
        except:
            db.rollback()
            raise



class TeamMember(Base, DefaultTable):
    user_id = Column(Integer, ForeignKey('User.id'), primary_key=True)
    team_id = Column(Integer, ForeignKey('Team.id'), primary_key=True)
    leader = Column(Boolean, default=False, nullable=False)
    # user = relationship('User')
    # team = relationship('Team')


class TeamInvitation(Base, DefaultTable):
    user_id = Column(Integer, ForeignKey('User.id'), primary_key=True)
    team_id = Column(Integer, ForeignKey('Team.id'), primary_key=True)


class Contest(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    public = Column(Boolean, nullable=False, default=False)
    start_time = Column(DateTime)
    duration = Column(Integer) # contest duration in minutes
    registration_start = Column(DateTime)
    registration_end = Column(DateTime)
    freeze_scoreboard = Column(Integer) # minutes after start_time
    max_team_size = Column(Integer, default=1)
    open_for_guests = Column(Boolean, nullable=False, default=True)
    # teams = relationship('Registration')
    # problems = relationship('ContestProblem', order_by="ContestProblem.short_id")

    def after_start(self, cur_time=None):
        cur_time = cur_time or datetime.datetime.now()
        return self.start_time <= cur_time

    def after_end(self, cur_time=None):
        cur_time = cur_time or datetime.datetime.now()
        return self.duration != None and self.start_time + datetime.timedelta(0, 60*self.duration) < cur_time

    def is_running(self, cur_time):
        cur_time = cur_time or datetime.datetime.now()
        return self.after_start(cur_time) and not self.after_end(cur_time)

    def after_registration_start(self, cur_time=None):
        cur_time = cur_time or datetime.datetime.now()
        return self.registration_start and self.registration_start < cur_time

    def after_registration_end(self, cur_time=None):
        cur_time = cur_time or datetime.datetime.now()
        return self.registration_end and self.registration_end < cur_time

    def is_registration_open(self, cur_time=None):
        cur_time = cur_time or datetime.datetime.now()
        return self.after_registration_start(cur_time) and not self.after_registration_end(cur_time)

    def is_registered(self, db, user):
        return db.query(Registration) \
                 .join(Team, Registration.team_id == Team.id) \
                 .join(TeamMember, Team.id == TeamMember.team_id) \
                 .filter(Registration.contest_id == self.id) \
                 .filter(TeamMember.user_id == user.id) \
                 .count() > 0

    def registration_count(self, db):
        return db.query(Registration) \
                 .filter_by(contest_id=self.id) \
                 .count()

    def elapsed(self, db, cur_time=None):
        cur_time = cur_time or datetime.datetime.now()
        return (cur_time - self.start_time).total_seconds() / 60 if self.start_time else None

    def get_problems(self, db, only_open=False, cur_time=None):
        res = db.query(ContestProblem) \
                .filter_by(contest_id=self.id) \

        if only_open and self.start_time:
            cur_time = cur_time or datetime.datetime.now()
            at = self.elapsed(cur_time)
            res = res.filter(and_( \
                        or_(ContestProblem.start_time == None, ContestProblem.start_time <= at), \
                        or_(ContestProblem.end_time == None, at <= ContestProblem.end_time)
                    ))

        res = res.order_by(ContestProblem.short_id)
        return res

    def get_problem(self, db, short_id):
        return db.query(ContestProblem) \
                 .filter_by(contest_id=self.id, short_id=short_id) \
                 .first()

    @staticmethod
    def get_public(db):
        return db.query(Contest) \
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

    def get_standings(self, db, cur_time=None):
        cur_time = cur_time or datetime.datetime.now()
        standings = {}

        for submission in db.query(Submission).filter_by(contest_id=self.id).filter(Submission.verdict.in_(['AC', 'WA', 'TLE', 'PE', 'RE', 'MLE'])).order_by(Submission.submitted):
            short_id = db.query(ContestProblem).filter_by(contest_id=self.id, problem_id=submission.problem_id).one().short_id
            # standings.setdefault(submission.team_id, [0, 0, {}])
            standings.setdefault(submission.team_id, {})
            standings[submission.team_id].setdefault(short_id, [0, None])
            if standings[submission.team_id][short_id][1] is not None: continue
            if submission.verdict == 'AC':
                # standings[submission.team_id][0] += 1
                # standings[submission.team_id][1] += submission.submitted
                standings[submission.team_id][short_id][1] = (submission.submitted - self.start_time).total_seconds() / 60.0
            else:
                # standings[submission.team_id][1] += 20
                standings[submission.team_id][short_id][0] += 1

        standings = [
            (
                Team.get_by_id(db, team_id),
                sum( 1 if ac_time else 0 for _, [_, ac_time] in problems.items() ),
                sum( 20*incorrect_tries + ac_time if ac_time else 0 for _, [incorrect_tries, ac_time] in problems.items() ) if self.start_time else 0,
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


class Registration(Base, DefaultTable):
    team_id = Column(Integer, ForeignKey('Team.id'), primary_key=True)
    contest_id = Column(Integer, ForeignKey('Contest.id'), primary_key=True)
    created = Column(DateTime, default=datetime.datetime.now, nullable=False)
    # team = relationship('Team')
    # contest = relationship('Contest')


class ProgrammingLanguage(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    compile_cmd = Column(String)
    run_cmd = Column(String, nullable=False)

    @staticmethod
    def get_by_id(db, id):
        return db.query(ProgrammingLanguage) \
                 .filter_by(id=id) \
                 .first()


class Problem(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    public = Column(Boolean, default=False, nullable=False)
    description = Column(Text, nullable=False)
    solution = Column(Text)
    solution_lang_id = Column(Integer, ForeignKey('ProgrammingLanguage.id'))
    checker = Column(Text)
    checker_lang_id = Column(Integer, ForeignKey('ProgrammingLanguage.id'))
    time_limit = Column(Integer) # milliseconds
    memory_limit = Column(Integer) # bytes
    # contests = relationship('ContestProblem')

    @staticmethod
    def get_by_id(db, id):
        return db.query(Problem).filter_by(id=id).first()

    def users_solved_count(self, db):
        return db.query(Submission.team_id) \
                 .filter_by(problem_id=self.id, contest_id=None, verdict='AC') \
                 .distinct() \
                 .count()

    def users_tried_count(self, db):
        return db.query(Submission.team_id) \
                 .filter_by(problem_id=self.id, contest_id=None) \
                 .distinct() \
                 .count()

    def get_tests(self, db):
        return db.query(Test) \
                 .filter_by(problem_id=self.id)

    @staticmethod
    def get_public(db):
        return db.query(Problem).filter(Problem.public).all()


class Test(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    problem_id = Column(Integer, ForeignKey('Problem.id'), nullable=False)
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=False)


# class Submission(Base, DefaultTable):
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('User.id'), nullable=False)
#     problem_id = Column(Integer, ForeignKey('Problem.id'), nullable=False)
#     submitted = Column(DateTime, default=datetime.datetime.now, nullable=False)
#     verdict = Column(Enum('Pending', 'WA', 'TLE', 'AC', 'PE', 'RE', 'MLE', 'SUBERR', name='submission_verdict'))
#     solution = Column(Text)
#     solution_lang_id = Column(Integer, ForeignKey('ProgrammingLanguage.id'))


class Submission(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('Team.id'), nullable=False)
    problem_id = Column(Integer, ForeignKey('Problem.id'), nullable=False)
    contest_id = Column(Integer, ForeignKey('Contest.id'))
    submitted = Column(DateTime, default=datetime.datetime.now, nullable=False)
    verdict = Column(Enum('Pending', 'WA', 'TLE', 'AC', 'PE', 'RE', 'MLE', 'SUBERR', name='submission_verdict'))
    solution = Column(Text, nullable=False)
    solution_lang_id = Column(Integer, ForeignKey('ProgrammingLanguage.id'), nullable=False)

    @staticmethod
    def get_by_id(db, id):
        return db.query(Submission) \
                 .filter_by(id=id) \
                 .first()


class JudgeQueue(Base, DefaultTable):
    submission_id = Column(Integer, ForeignKey('Submission.id'), primary_key=True)
    last_announce = Column(DateTime)

    ANNOUNCE_TIMEOUT = 30 * 1000 # ms
    REAL_ANNOUNCE_TIMEOUT = 60 * 1000 # ms

    @staticmethod
    def get_next(db, contest_id=None, any_contest=False):
        # TODO: Make sure each client gets a different submission

        trans = db.begin(subtransactions=True)
        try:
            res = db.query(JudgeQueue) \
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

    @staticmethod
    def get_by_submission_id(db, submission_id):
        return db.query(JudgeQueue) \
                 .filter_by(submission_id=submission_id) \
                 .first()


class ContestProblem(Base, DefaultTable):
    short_id = Column(String, nullable=False)
    problem_id = Column(Integer, ForeignKey('Problem.id'), primary_key=True)
    contest_id = Column(Integer, ForeignKey('Contest.id'), primary_key=True)
    start_time = Column(Integer) # minutes after contest.start_time
    end_time = Column(Integer) # minutes after contest.start_time
    # problem = relationship('Problem')
    # contest = relationship('Contest')

    __table_args__ = (
        UniqueConstraint('short_id', 'contest_id'),
    )

    @staticmethod
    def get_by_id(db, problem_id, contest_id):
        return db.query(ContestProblem) \
                 .filter_by(problem_id=problem_id, contest_id=contest_id) \
                 .first()

    def get_problem(self, db):
        return db.query(Problem) \
                 .filter_by(id=self.problem_id) \
                 .first()

    def is_open(self, elapsed):
        return (not self.start_time or elapsed >= self.start_time) and (not self.end_time or self.end_time <= elapsed)

    def teams_solved_count(self, db):
        return db.query(Submission.team_id).filter_by(contest_id=self.contest_id, problem_id=self.problem_id, verdict='AC').distinct().count()

    def teams_tried_count(self, db):
        return db.query(Submission.team_id).filter_by(contest_id=self.contest_id, problem_id=self.problem_id).distinct().count()


class ProblemComment(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.id'), nullable=False)
    problem_id = Column(Integer, ForeignKey('Problem.id'), nullable=False)
    created = Column(DateTime, default=datetime.datetime.now, nullable=False)
    content = Column(Text, nullable=False)


class ProblemCommentLike(Base, DefaultTable):
    user_id = Column(Integer, primary_key=True)
    problem_comment_id = Column(Integer, ForeignKey('ProblemComment.id'), primary_key=True)


class Message(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    user_to_id = Column(Integer, ForeignKey('User.id'), nullable=False)
    user_from_id = Column(Integer, ForeignKey('User.id'))
    subject = Column(String)
    content = Column(Text, nullable=False)
    read = Column(Boolean, default=False, nullable=False)
    sent = Column(DateTime, default=datetime.datetime.now, nullable=False)

    def get_user_to(self, db):
        return db.query(User).filter_by(id=self.user_to_id).first()

    def get_user_from(self, db):
        return db.query(User).filter_by(id=self.user_from_id).first()


class Permission(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class PermissionGroup(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class PermissionGroupUser(Base, DefaultTable):
    permission_group_id = Column(Integer, ForeignKey('PermissionGroup.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('User.id'), primary_key=True)

