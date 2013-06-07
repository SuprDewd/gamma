from base import BaseHandler
from ui_modules import PaginationModule
import datetime
from models import Contest

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

        def is_current_user_registered(contest):
            return self.current_user and contest.is_registered(sess, self.current_user)

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
                    current_contests=current_contests,
                    is_current_user_registered=is_current_user_registered,
                    format_date=self.locale.format_date)

class ContestRegisterHandler(BaseHandler):
    def get(self, contest=None):
        # Remember to check if contest is public
        pass

    def get(self, contest=None):
        # Remember to check if contest is public
        pass
