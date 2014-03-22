# coding: utf8
import unittest
from tornado.web import Application
from tornado.testing import AsyncHTTPTestCase, LogTrapTestCase, main
import tornado.locale

from models import *
from queries import Queries

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('sqlite://', convert_unicode=True)
db_session = sessionmaker(bind=engine)
locale = tornado.locale.get('en_US')
salt='abc'


class FakeApplication:
    def __init__(self):
        self.db = db_session
        self.options = {
            'cookie_secret': salt
        }

class FakeRequestHandler:
    def __init__(self):
        self.application = FakeApplication()
        self.locale = locale


class SQLAlchemyTestCase:
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.q = Queries(FakeRequestHandler())

    def tearDown(self):
        self.q.close()
        Base.metadata.drop_all(bind=engine)


class UserModelTestCase(AsyncHTTPTestCase, LogTrapTestCase, SQLAlchemyTestCase):
    def get_app(self):
        return Application([])

    def setUp(self):
        SQLAlchemyTestCase.setUp(self)
        AsyncHTTPTestCase.setUp(self)

    def tearDown(self):
        SQLAlchemyTestCase.tearDown(self)

    def test_validate_valid_returns_no_errors(self):
        res = self.q.User_validate(
            username='SuprDewd',
            email='suprdewd@gmail.com',
            name=r'Bjarki Ágúst Guðmundsson',
            institute=r'Háskólinn í Reykjavík',
            password='Test123',
            password_confirm='Test123')

        self.assertEqual(res, {})

    def test_validate_long_username_returns_errors(self):
        res = self.q.User_validate(
            username='X' * 20,
            email='suprdewd@gmail.com',
            name=r'Bjarki Ágúst Guðmundsson',
            institute=r'Háskólinn í Reykjavík',
            password='Test123',
            password_confirm='Test123')

        self.assertEqual(res, {})

        res = self.q.User_validate(
            username='X' * 21,
            email='suprdewd@gmail.com',
            name=r'Bjarki Ágúst Guðmundsson',
            institute=r'Háskólinn í Reykjavík',
            password='Test123',
            password_confirm='Test123')

        self.assertEqual(res.keys(), ['username'])
        self.assertIn('Username too long', res['username'])

    def test_validate_short_username_returns_errors(self):
        res = self.q.User_validate(
            username='X' * 3,
            email='suprdewd@gmail.com',
            name=r'Bjarki Ágúst Guðmundsson',
            institute=r'Háskólinn í Reykjavík',
            password='Test123',
            password_confirm='Test123')

        self.assertEqual(res, {})

        res = self.q.User_validate(
            username='X' * 2,
            email='suprdewd@gmail.com',
            name=r'Bjarki Ágúst Guðmundsson',
            institute=r'Háskólinn í Reykjavík',
            password='Test123',
            password_confirm='Test123')

        self.assertEqual(res.keys(), ['username'])
        self.assertIn('Username too short', res['username'])

    def test_validate_user_taken(self):
        self.q.User_register(
            username='SuprDewd',
            email='suprdewd@gmail.com',
            name=u'Bjarki Ágúst Guðmundsson',
            institute=u'Háskólinn í Reykjavík',
            password='Test123')

        res = self.q.User_validate(
            username='SuprDewd',
            email='suprdewd@gmail.com',
            name=r'Bjarki Ágúst Guðmundsson',
            institute=r'Háskólinn í Reykjavík',
            password='Test123',
            password_confirm='Test123')

        self.assertEqual(res.keys(), ['username'])
        self.assertIn('Username is taken', res['username'])

    def test_register(self):
        user = self.q.User_register(
            username='SuprDewd',
            email='suprdewd@gmail.com',
            name=u'Bjarki Ágúst Guðmundsson',
            institute=u'Háskólinn í Reykjavík',
            password='Test123')

        self.assertIsNotNone(user)
        self.assertIs(self.q.db.query(User).filter_by(username='SuprDewd').first(), user)

        self.assertFalse(user.active)

        team = self.q.db.query(Team).filter_by(name='SuprDewd').first()
        self.assertIsNotNone(team)

        self.assertTrue(team.locked)

        team_member = self.q.db.query(TeamMember).filter_by(user_id=user.id, team_id=team.id).first()
        self.assertIsNotNone(team_member)
        self.assertEqual(team_member.team_id, team.id)
        self.assertEqual(team_member.user_id, user.id)
        self.assertTrue(team_member.leader)

        self.assertEqual(self.q.User_get_teams(user).all(), [team])
        self.assertEqual(self.q.User_get_teams(user, only_led_by_me=True).all(), [team])
        self.assertEqual(self.q.Team_get_members(team).all(), [team_member])

    def test_login(self):
        user = self.q.User_register(
            username='SuprDewd',
            email='suprdewd@gmail.com',
            name=u'Bjarki Ágúst Guðmundsson',
            institute=u'Háskólinn í Reykjavík',
            password='Test123')

        self.assertIsNone(self.q.User_login('SuprDewd', 'Test123'))
        self.assertIsNone(self.q.User_login('SuprDewd', 'Test12'))
        self.assertIsNone(self.q.User_login('SuprDewd', ''))
        self.assertIsNone(self.q.User_login('SuprDew', 'Test123'))
        self.assertIsNone(self.q.User_login('', 'Test123'))

        user.active = True

        self.assertEqual(self.q.User_login('SuprDewd', 'Test123'), user)
        self.assertIsNone(self.q.User_login('SuprDewd', 'Test12'))
        self.assertIsNone(self.q.User_login('SuprDewd', ''))
        self.assertIsNone(self.q.User_login('SuprDew', 'Test123'))
        self.assertIsNone(self.q.User_login('', 'Test123'))


class ProblemModelTestCase(AsyncHTTPTestCase, LogTrapTestCase, SQLAlchemyTestCase):
    def get_app(self):
        return Application([])

    def setUp(self):
        SQLAlchemyTestCase.setUp(self)
        AsyncHTTPTestCase.setUp(self)

    def tearDown(self):
        SQLAlchemyTestCase.tearDown(self)


if __name__ == '__main__':
    unittest.main()
