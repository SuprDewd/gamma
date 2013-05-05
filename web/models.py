from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM as Enum
from sqlalchemy.orm import relationship, backref, sessionmaker

Base = declarative_base()

def init_db(engine):
    Base.metadata.create_all(bind=engine)


class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password_hash = Column(String, nullable=True)
    email = Column(String, nullable=False)
    confirmed = Column(Boolean, nullable=False)
    confirm_token = Column(String, nullable=True)
    confirm_expires = Column(DateTime, nullable=True)
    name = Column(String, nullable=True)
    role = Column(Enum('admin', 'user', 'judge', name='role_type'), nullable=False)

    __table_args__ = (
        UniqueConstraint('username'),
        UniqueConstraint('email'),
        UniqueConstraint('confirm_token'),
    )


class Contest(Base):
    __tablename__ = 'Contest'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=True)
    length = Column(Integer, nullable=True) # contest length in minutes
    registration_start = Column(DateTime, nullable=True)
    registration_end = Column(DateTime, nullable=True)
    freeze_scoreboard = Column(Integer, nullable=True) # minutes after start_time


class Registration(Base):
    __tablename__ = 'Registration'

    user_id = Column(Integer, ForeignKey('User.id'))
    contest_id = Column(Integer, ForeignKey('Contest.id'))
    created = Column(DateTime, nullable=False)

    __table_args__ = (
        #FIXME: Create a compound primary key: PrimaryKey('user_id', 'contest_id'),
    )


class Problem(Base):
    __tablename__ = 'Problem'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    public = Column(Boolean, nullable=False)
    description_file = Column(String, nullable=False)
    solution_file = Column(String, nullable=True)
    checker_file = Column(String, nullable=True)
    judge = Column(Enum('manual', 'automatic_diff', 'automatic_checker', name='judge_type'), nullable=True)


class Test(Base):
    __tablename__ = 'Test'

    id = Column(Integer, primary_key=True)
    problem_id = Column(String, nullable=False)
    input_file = Column(String, nullable=False)
    output_file = Column(String, nullable=False)


class UserSolve(Base):
    __tablename__ = 'UserSolve'

    user_id = Column(Integer, ForeignKey('User.id'))
    problem_id = Column(Integer, ForeignKey('Problem.id'))
    contest_id = Column(Integer, ForeignKey('Contest.id'), nullable=True)
    solve_at = Column(Integer, nullable=True)

    __table_args__ = (
        #FIXME: Create a compound primary key: PrimaryKey('user_id', 'problem_id'),
        #FIXME: What happens when a user solves a problem before contest start? Shouldn't he be allowed to solve it?
    )


class ContestProblem(Base):
    __tablename__ = 'ContestProblem'

    short_id = Column(String, nullable=False)
    problem_id = Column(Integer, ForeignKey('Problem.id'))
    contest_id = Column(Integer, ForeignKey('Contest.id'))
    appear_time = Column(Integer, nullable=True)  # minutes after contest.start_time

    __table_args__ = (
        #FIXME: Create a compound primary key: PrimaryKey('problem_id', 'contest_id')
        UniqueConstraint('short_id', 'contest_id'),
    )


class Solution(Base):
    __tablename__ = 'Solution'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.id'), nullable=True)
    problem_id = Column(Integer, ForeignKey('Problem.id'))


class SolutionLike(Base):
    __tablename__ = 'SolutionLike'

    user_id = Column(Integer, ForeignKey('User.id'))
    solution_id = Column(Integer, ForeignKey('Solution.id'))

    __table_args__ = (
        #FIXME: Create a compound primary key: PrimaryKey('user_id', 'solution_id')
    )


class SolutionComment(Base):
    __tablename__ = 'SolutionComment'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.id'))
    solution_id = Column(Integer, ForeignKey('Solution.id'))
    created = Column(DateTime, nullable=False)
    content = Column(Text, nullable=False)

