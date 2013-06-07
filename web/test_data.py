from models import *
import datetime
import random

def add_test_data(db):

    cnt = 100
    splt = cnt - 20

    for i in range(cnt):
        db.add(Contest(name='Test Contest %d' % i,
                       public=True,
                       start_time=datetime.datetime.now() - datetime.timedelta(splt) + datetime.timedelta(i),
                       duration=2 * 60 + 30,
                       registration_start=datetime.datetime.now() - datetime.timedelta(splt) + datetime.timedelta(i-10),
                       registration_end=datetime.datetime.now() - datetime.timedelta(splt) + datetime.timedelta(i-1)))

    db.commit()

    cnt = 30

    for i in range(cnt):
        db.add(Problem(name='Test Problem %d' % i,
                       public=True,
                       description='test'))

    db.commit()

    # cnt = 30

    # for i in range(cnt):
    #     db.add(ContestSubmission(team_id=random.randint(1, 10),
    #                              problem_id=random.randint(1, cnt-1),
    #                              contest_id=None,
    #                              verdict='AC' if random.randint(0, 1) == 0 else 'WA'))

    # db.commit()

