from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
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
    email = Column(String(200), nullable=False)
    name = Column(String)
    institute = Column(String)
    api_key = Column(String)
    registered = Column(DateTime, default=datetime.datetime.now)
    active = Column(Boolean, default=False)
    confirm_token = Column(String, default=util.generate_confirm_token, unique=True)
    teams = relationship('TeamMember')
    # main_team_id = Column(Integer, ForeignKey('Team.id'))

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

            if create_main_team:
                db.flush()
                team = Team(name=username, locked=True)
                db.add(team)
                db.flush()
                team_member = TeamMember(user_id=user.id, team_id=team.id, leader=True)
                db.add(team_member)

            db.commit()
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


class Team(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    locked = Column(Boolean, nullable=False, default=False)
    members = relationship('TeamMember')
    contests = relationship('Registration')


class TeamMember(Base, DefaultTable):
    user_id = Column(Integer, ForeignKey('User.id'), primary_key=True)
    team_id = Column(Integer, ForeignKey('Team.id'), primary_key=True)
    leader = Column(Boolean, default=False, nullable=False)
    user = relationship('User')
    team = relationship('Team')


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
    teams = relationship('Registration')
    problems = relationship('ContestProblem', order_by="ContestProblem.short_id")

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

    def is_registered(self, sess, user):
        return sess.query(Registration).join(Team, Registration.team_id == Team.id).join(TeamMember, Team.id == TeamMember.team_id).filter(Registration.contest_id == self.id).filter(TeamMember.user_id == user.id).count() > 0

    def registration_count(self, sess):
        return sess.query(Registration).filter_by(contest_id=self.id).count()

    @staticmethod
    def get_public(db):
        return db.query(Contest).filter(Contest.public).all()

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

    def get_standings(self, db):
        standings = []
        for team in self.teams:
            points = 0
            penalty = 0
            summary = []
            for problem in self.problems:
                first_ac = db.query(ContestSubmission).filter_by(team_id=team.team_id, contest_id=self.id, problem_id=problem.problem_id, verdict='AC').order_by(ContestSubmission.submitted).first()
                count = db.query(ContestSubmission).filter_by(team_id=team.team_id, contest_id=self.id, problem_id=problem.problem_id).filter(ContestSubmission.verdict.in_(['WA', 'TLE', 'PE', 'RE', 'MLE']))
                if first_ac: count = count.filter(ContestSubmission.submitted <= first_ac.submitted)
                count = count.count()
                if first_ac:
                    points += 1
                    penalty += 20 * count
                summary.append((first_ac.submitted if first_ac else None, count))
            standings.append({'points': points, 'penalty': penalty, 'team': team.team, 'problems': summary})

        def comparer(a, b):
            if a['points'] != b['points']: return -cmp(a['points'], b['points'])
            if a['penalty'] != b['penalty']: return cmp(a['penalty'], b['penalty'])
            return 0
        standings.sort(comparer)
        return standings

class Registration(Base, DefaultTable):
    team_id = Column(Integer, ForeignKey('Team.id'), primary_key=True)
    contest_id = Column(Integer, ForeignKey('Contest.id'), primary_key=True)
    created = Column(DateTime, default=datetime.datetime.now, nullable=False)
    team = relationship('Team')
    contest = relationship('Contest')


class ProgrammingLanguage(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    compile_cmd = Column(String)
    run_cmd = Column(String, nullable=False)


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
    contests = relationship('ContestProblem')

    def total_submission_count(self, db):
        return db.query(Submission).filter_by(problem_id=self.id).count()

    def correct_submission_count(self, db):
        return db.query(Submission).filter_by(problem_id=self.id, verdict='AC').count()

    @staticmethod
    def get_public(db):
        return db.query(Problem).filter(Problem.public).all()


class Test(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    problem_id = Column(Integer, ForeignKey('Problem.id'), nullable=False)
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=False)


class Submission(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.id'), nullable=False)
    problem_id = Column(Integer, ForeignKey('Problem.id'), nullable=False)
    submitted = Column(DateTime, default=datetime.datetime.now, nullable=False)
    verdict = Column(Enum('Pending', 'WA', 'TLE', 'AC', 'PE', 'RE', 'MLE', 'SUBERR', name='submission_verdict'))
    solution = Column(Text)
    solution_lang_id = Column(Integer, ForeignKey('ProgrammingLanguage.id'))


class ContestSubmission(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('Team.id'), nullable=False)
    problem_id = Column(Integer, ForeignKey('Problem.id'), nullable=False)
    contest_id = Column(Integer, ForeignKey('Contest.id'), nullable=False)
    submitted = Column(Integer, nullable=False) # minutes after contest.start_time
    verdict = Column(Enum('Pending', 'WA', 'TLE', 'AC', 'PE', 'RE', 'MLE', 'SUBERR', name='contest_submission_verdict'))
    solution = Column(Text, nullable=False)
    solution_lang_id = Column(Integer, ForeignKey('ProgrammingLanguage.id'), nullable=False)


class ContestProblem(Base, DefaultTable):
    short_id = Column(String, nullable=False)
    problem_id = Column(Integer, ForeignKey('Problem.id'), primary_key=True)
    contest_id = Column(Integer, ForeignKey('Contest.id'), primary_key=True)
    start_time = Column(Integer) # minutes after contest.start_time
    end_time = Column(Integer) # minutes after contest.start_time
    problem = relationship('Problem')
    contest = relationship('Contest')

    __table_args__ = (
        UniqueConstraint('short_id', 'contest_id'),
    )


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
    content = Column(Text, nullable=False)
    read = Column(Boolean, default=False, nullable=False)
    sent = Column(DateTime, default=datetime.datetime.now, nullable=False)


class Permission(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class PermissionGroup(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class PermissionGroupUser(Base, DefaultTable):
    permission_group_id = Column(Integer, ForeignKey('PermissionGroup.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('User.id'), primary_key=True)

