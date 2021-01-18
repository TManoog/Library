import configparser
from datetime import timedelta
from time import time

import utilities
from entities import Book, User, CheckoutInfo

ONE_WEEK = timedelta(weeks=1).total_seconds()
THREE_MONTHS = timedelta(days=90).total_seconds()


class LibraryCatalog:
    def __init__(self, books_path, users_path, checkout_info_path, overdue_time=THREE_MONTHS, overdue_rate=5,
                 auto_persist: bool = True):
        self.__overdue_rate = overdue_rate
        self.__overdue_time = overdue_time
        self.__checkout_infos_path = checkout_info_path
        self.__users_path = users_path
        self.__books_path = books_path

        self.__books = configparser.ConfigParser()
        self.__users = configparser.ConfigParser()
        self.__checkout_infos = configparser.ConfigParser()

        self.__books.read(books_path)
        self.__users.read(users_path)
        self.__checkout_infos.read(checkout_info_path)

        self.__auto_persist = auto_persist

    def user_checkout_book(self, user_id, book_isbn):
        check_isbn = lambda isbn: isbn == book_isbn
        books = utilities.find_in_config(self.__books, [(None, check_isbn)])
        if len(books) < 0:
            raise AssertionError("No book with such ISBN: " + book_isbn)

        book_info: CheckoutInfo = self.__get_checkout_info(book_isbn)
        if int(book_info.available_count) <= 0:
            raise AssertionError("Required book is unavailable.")
        if user_id in book_info.checkouted_user_ids:
            raise AssertionError("This user already checked out the book")

        if user_id in book_info.reserved_user_ids:
            book_info.reserved_user_ids.remove(user_id)

        book_info.checkouted_user_ids.append(user_id)
        book_info.checkout_dates.append(str(time()))
        book_info.available_count = int(book_info.available_count) - 1

        utilities.store_in_config(self.__checkout_infos, book_info)
        self.__do_auto_persist(self.__checkout_infos, self.__checkout_infos_path)

    def user_return_book(self, user_id, book_isbn):
        book_info: CheckoutInfo = self.__get_checkout_info(book_isbn)
        book_info.available_count = int(book_info.available_count) + 1
        user_idx = book_info.checkouted_user_ids.index(user_id)
        book_info.checkouted_user_ids.pop(user_idx)
        book_info.checkout_dates.pop(user_idx)

        if book_info.available_count == 1:
            self.__notify_users(book_info)

        utilities.store_in_config(self.__checkout_infos, book_info)
        self.__do_auto_persist(self.__checkout_infos, self.__checkout_infos_path)

    def user_reserve_book(self, user_id, book_isbn):
        book_info = self.__get_checkout_info(book_isbn)
        book_info.reserved_user_ids.append(user_id)

        utilities.store_in_config(self.__checkout_infos, book_info)
        self.__do_auto_persist(self.__checkout_infos, self.__checkout_infos_path)

    def get_subscribers_of_the_book(self, book_id):
        book_info: CheckoutInfo = self.__get_checkout_info(book_id)

        is_user_reserved = lambda id: id in book_info.reserved_user_ids
        users = utilities.find_in_config(self.__users,
                                         [(None, is_user_reserved)],
                                         User)
        return users

    def get_notifications_for_reserved_books(self, user_id):
        id_equals = lambda id: id == user_id
        user: User = utilities.find_in_config(self.__users,
                                              [(None, id_equals)],
                                              User)[0]

        # delete notifications
        user.notifications = set()
        utilities.store_in_config(self.__users, user)
        self.__do_auto_persist(self.__users, self.__users_path)

        return user.notifications

    def get_overdue_books_of_the_user(self, user_id):
        contains_id = lambda id_list: user_id in id_list
        infos = utilities.find_in_config(self.__checkout_infos,
                                         [("checkouted_user_ids", contains_id)],
                                         CheckoutInfo)
        curr_time = time()
        result = []
        for i in infos:
            info: CheckoutInfo = i
            user_idx = info.checkouted_user_ids.index(user_id)
            checkout_time = float(info.checkout_dates[user_idx])
            if curr_time - checkout_time > self.__overdue_time:
                result.append(info.book_id)

        contains_isbn = lambda isbn: isbn in result
        return utilities.find_in_config(self.__books,
                                        [(None, contains_isbn)],
                                        Book)

    def get_fine_for_overdue_book_of_the_user(self, user_id, book_isbn):
        check_isbn = lambda isbn: isbn == book_isbn
        info: CheckoutInfo = utilities.find_in_config(self.__checkout_infos,
                                                      [(None, check_isbn)],
                                                      CheckoutInfo)[0]
        user_idx = info.checkouted_user_ids.index(user_id)
        user_checkout_time = float(info.checkout_dates[user_idx])
        return int((time() - user_checkout_time) / ONE_WEEK) * self.__overdue_rate

    def get_total_fine(self, user_id):
        contains_id = lambda id_list: user_id in id_list
        infos = utilities.find_in_config(self.__checkout_infos,
                                         [("checkouted_user_ids", contains_id)],
                                         CheckoutInfo)
        curr_time = time()
        times = []
        for i in infos:
            info: CheckoutInfo = i
            user_idx = info.checkouted_user_ids.index(user_id)
            checkout_time = float(info.checkout_dates[user_idx])
            if curr_time - checkout_time > self.__overdue_time:
                times.append(curr_time - checkout_time)

        result = 0
        for t in times:
            result += int((t - self.__overdue_time) / ONE_WEEK) * self.__overdue_rate

        return result

    def check_book_is_available(self, book_isbn):
        book_info = self.__get_checkout_info(book_isbn)
        return int(book_info.available_count) > 0

    def get_users_who_checked_out_book(self, book_isbn):
        book_info = self.__get_checkout_info(book_isbn)
        is_user_checkouted = lambda id: id in book_info.checkouted_user_ids
        users: User = utilities.find_in_config(self.__users,
                                               [(None, is_user_checkouted)],
                                               User)
        return users

    def add_user(self, user):
        utilities.store_in_config(self.__users, user)
        self.__do_auto_persist()

    def add_book(self, book, count):
        checkout_info: CheckoutInfo = self.__get_checkout_info(book)
        if checkout_info is not None:
            checkout_info.count = int(checkout_info.count) + count
            checkout_info.available_count = int(checkout_info.available_count) + count
        else:
            utilities.store_in_config(self.__books, book)
            checkout_info = CheckoutInfo(book.isbn, count, count)
        utilities.store_in_config(self.__checkout_infos, checkout_info)

        self.__do_auto_persist(self.__books, self.__books_path)
        self.__do_auto_persist(self.__checkout_infos, self.__checkout_infos_path)

    def remove_user(self, user_id):
        utilities.remove_from_config(self.__users, user_id)
        self.__do_auto_persist(self.__users, self.__users_path)

    def remove_book(self, book_isbn):
        utilities.remove_from_config(self.__books, book_isbn)
        utilities.remove_from_config(self.__checkout_infos, book_isbn)
        self.__do_auto_persist(self.__books, self.__books_path)
        self.__do_auto_persist(self.__checkout_infos, self.__checkout_infos_path)

    def persist_everything(self):
        utilities.store_config(self.__books, self.__books_path)
        utilities.store_config(self.__users, self.__users_path)
        utilities.store_config(self.__checkout_infos, self.__checkout_infos_path)

    def __do_auto_persist(self, config=None, path=None):
        if self.__auto_persist:
            if config is None:
                self.persist_everything()
            else:
                utilities.store_config(config, path)

    def __notify_users(self, book_info):
        is_user_reserved = lambda id: id in book_info.reserved_user_ids
        users = utilities.find_in_config(self.__users,
                                         [(None, is_user_reserved)],
                                         User)
        for user in users:
            user.notifications.add(book_info.book_id)
            utilities.store_in_config(self.__users, user)

        self.__do_auto_persist(self.__users, self.__users_path)

    def __get_checkout_info(self, book_isbn):
        check_isbn = lambda isbn: isbn == book_isbn
        book_info_list = utilities.find_in_config(self.__checkout_infos,
                                                  [(None, check_isbn)],
                                                  CheckoutInfo)
        if len(book_info_list) > 0:
            return book_info_list[0]
        return None
