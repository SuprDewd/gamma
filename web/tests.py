# coding: utf8
import unittest
from tornado.web import Application
from tornado.testing import AsyncHTTPTestCase, LogTrapTestCase, main
import tornado.locale

from models import *

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('sqlite://', convert_unicode=True)
db_session = sessionmaker(bind=engine)
locale = tornado.locale.get('en_US')
salt='abc'


class SQLAlchemyTestCase:
    def setUp(self):
        Base.metadata.create_all(bind=engine)

    def tearDown(self):
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
        sess = db_session()

        res = User.validate(sess, locale,
            username='SuprDewd',
            email='suprdewd@gmail.com',
            name=r'Bjarki Ágúst Guðmundsson',
            institute=r'Háskólinn í Reykjavík',
            password='Test123',
            password_confirm='Test123')

        self.assertEqual(res, {})


    def test_validate_long_username_returns_errors(self):
        sess = db_session()

        res = User.validate(sess, locale,
            username='X' * 20,
            email='suprdewd@gmail.com',
            name=r'Bjarki Ágúst Guðmundsson',
            institute=r'Háskólinn í Reykjavík',
            password='Test123',
            password_confirm='Test123')

        self.assertEqual(res, {})

        res = User.validate(sess, locale,
            username='X' * 21,
            email='suprdewd@gmail.com',
            name=r'Bjarki Ágúst Guðmundsson',
            institute=r'Háskólinn í Reykjavík',
            password='Test123',
            password_confirm='Test123')

        self.assertEqual(res.keys(), ['username'])
        self.assertIn('Username too long', res['username'])

    def test_validate_short_username_returns_errors(self):
        sess = db_session()

        res = User.validate(sess, locale,
            username='X' * 3,
            email='suprdewd@gmail.com',
            name=r'Bjarki Ágúst Guðmundsson',
            institute=r'Háskólinn í Reykjavík',
            password='Test123',
            password_confirm='Test123')

        self.assertEqual(res, {})

        res = User.validate(sess, locale,
            username='X' * 2,
            email='suprdewd@gmail.com',
            name=r'Bjarki Ágúst Guðmundsson',
            institute=r'Háskólinn í Reykjavík',
            password='Test123',
            password_confirm='Test123')

        self.assertEqual(res.keys(), ['username'])
        self.assertIn('Username too short', res['username'])

    def test_validate_user_taken(self):
        sess = db_session()

        User.register(sess,
            username='SuprDewd',
            email='suprdewd@gmail.com',
            name=u'Bjarki Ágúst Guðmundsson',
            institute=u'Háskólinn í Reykjavík',
            password='Test123',
            salt=salt)

        res = User.validate(sess, locale,
            username='SuprDewd',
            email='suprdewd@gmail.com',
            name=r'Bjarki Ágúst Guðmundsson',
            institute=r'Háskólinn í Reykjavík',
            password='Test123',
            password_confirm='Test123')

        self.assertEqual(res.keys(), ['username'])
        self.assertIn('Username is taken', res['username'])

    def test_register(self):
        sess = db_session()

        user = User.register(sess,
            username='SuprDewd',
            email='suprdewd@gmail.com',
            name=u'Bjarki Ágúst Guðmundsson',
            institute=u'Háskólinn í Reykjavík',
            password='Test123',
            salt=salt)

        self.assertIsNotNone(user)
        self.assertIs(sess.query(User).filter_by(username='SuprDewd').first(), user)

        self.assertFalse(user.active)

        team = sess.query(Team).filter_by(name='SuprDewd').first()
        self.assertIsNotNone(team)

        self.assertTrue(team.locked)

        team_member = sess.query(TeamMember).filter_by(user_id=user.id, team_id=team.id).first()
        self.assertIsNotNone(team_member)
        self.assertIs(team_member.team, team)
        self.assertIs(team_member.user, user)
        self.assertTrue(team_member.leader)

        self.assertEqual(user.teams, [team_member])
        self.assertEqual(team.members, [team_member])

    def test_login(self):
        sess = db_session()

        user = User.register(sess,
            username='SuprDewd',
            email='suprdewd@gmail.com',
            name=u'Bjarki Ágúst Guðmundsson',
            institute=u'Háskólinn í Reykjavík',
            password='Test123',
            salt=salt)

        self.assertIsNone(User.login(sess, 'SuprDewd', 'Test123', salt))
        self.assertIsNone(User.login(sess, 'SuprDewd', 'Test12', salt))
        self.assertIsNone(User.login(sess, 'SuprDewd', '', salt))
        self.assertIsNone(User.login(sess, 'SuprDew', 'Test123', salt))
        self.assertIsNone(User.login(sess, '', 'Test123', salt))

        user.active = True

        self.assertEqual(User.login(sess, 'SuprDewd', 'Test123', salt), user)
        self.assertIsNone(User.login(sess, 'SuprDewd', 'Test12', salt))
        self.assertIsNone(User.login(sess, 'SuprDewd', '', salt))
        self.assertIsNone(User.login(sess, 'SuprDew', 'Test123', salt))
        self.assertIsNone(User.login(sess, '', 'Test123', salt))


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
