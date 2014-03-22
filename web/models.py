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


class Team(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    locked = Column(Boolean, nullable=False, default=False)
    # members = relationship('TeamMember')
    # contests = relationship('Registration')


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


class JudgeQueue(Base, DefaultTable):
    submission_id = Column(Integer, ForeignKey('Submission.id'), primary_key=True)
    last_announce = Column(DateTime)

    ANNOUNCE_TIMEOUT = 30 * 1000 # ms
    REAL_ANNOUNCE_TIMEOUT = 60 * 1000 # ms


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


class Permission(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class PermissionGroup(Base, DefaultTable):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class PermissionGroupUser(Base, DefaultTable):
    permission_group_id = Column(Integer, ForeignKey('PermissionGroup.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('User.id'), primary_key=True)

