import utilities


class Entity:
    def get_section_info(self):
        pass

    def get_section_attributes(self):
        pass

    def reformat(self):
        pass


class Book(Entity):
    def __init__(self, isbn=None, title=None, pages=None):
        self.isbn = isbn
        self.title = title
        self.pages = pages

    def get_section_info(self):
        return ["isbn", self.isbn]

    def get_section_attributes(self):
        return ["title", "pages"]

    def reformat(self):
        self.pages = int(self.pages)

    def __repr__(self):
        return self.title


class User(Entity):
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name
        self.notifications = set()

    def get_section_info(self):
        return ["id", self.id]

    def get_section_attributes(self):
        return ["name", "notifications"]

    def reformat(self):
        self.notifications = utilities.string_to_set(self.notifications)


class CheckoutInfo(Entity):
    def __init__(self, book_id=None, count=None, available_count=None):
        self.book_id = book_id
        self.count = count
        self.available_count = available_count
        self.checkouted_user_ids = []
        self.checkout_dates = []
        self.reserved_user_ids = []

    def get_section_info(self):
        return ["book_id", self.book_id]

    def get_section_attributes(self):
        return ["count", "available_count", "checkouted_user_ids", "checkout_dates", "reserved_user_ids"]

    def reformat(self):
        self.count = int(self.count)
        self.available_count = int(self.available_count)

        self.checkouted_user_ids = utilities.string_to_list(self.checkouted_user_ids)
        self.checkout_dates = utilities.string_to_list(self.checkout_dates)
        self.reserved_user_ids = utilities.string_to_list(self.reserved_user_ids)
