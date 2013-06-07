import tornado.web

class PaginationModule(tornado.web.UIModule):
    def render(self, item_count, cur_page, items_per_page, page_location):
        return self.render_string('ui_modules/pagination.html',
                    cur_page=cur_page,
                    total_pages=item_count/items_per_page + (0 if item_count % items_per_page == 0 else 1),
                    page_location=page_location)

    @staticmethod
    def current_items(items, cur_page, items_per_page):
        at = cur_page*items_per_page
        return items[at:at+items_per_page]
