from base import BaseHandler
from pagination import PaginationModule
import datetime
from models import Contest

class AllContestsHandler(BaseHandler):
    def get(self, cur_page=None):
        contests = self.application.db.query(Contest).all()
        old_contests = []
        cur_contests = []

        for c in contests:
            if c.start_time + datetime.timedelta(0, 60 * c.length) < datetime.datetime.now():
                old_contests.append(c)
            else:
                cur_contests.append(c)

        cur_page = int(cur_page) if cur_page else 0
        items_per_page = 10
        page_location = '/contests/%d/'

        return self.render('all_contests.html',
                    cur_page=cur_page,
                    item_count=len(old_contests),
                    items_per_page=items_per_page,
                    page_location=page_location,
                    old_contests=PaginationModule.current_items(old_contests, cur_page, items_per_page),
                    cur_contests=cur_contests)
