from entities import Book, User
from library_catalog import LibraryCatalog

if __name__ == '__main__':
    catalog = LibraryCatalog("configs/books.ini",
                             "configs/users.ini",
                             "configs/checkout_info.ini")

    b1 = Book("0156012197", "The Little Prince", "93")
    b2 = Book("0140449264", "The Count of Monte Cristo", "1276")
    # catalog.remove_book(b2.isbn)
    # catalog.add_book(b1, count=4)
    # catalog.add_book(b2, count=3)
    u1 = User("1", "Tata")
    u2 = User("2", "John")
    # catalog.add_user(u1)
    # catalog.remove_user("1")
    # catalog.add_user(u2)
    # catalog.add_book(b2, 1)

    try:
        pass
        # catalog.user_checkout_book(u1.id, b1.isbn)
        # catalog.user_checkout_book(u1.id, b2.isbn)
    except AssertionError as e:
        print(e)

    # catalog.user_reserve_book(u2.id, b1.isbn)
    # catalog.user_return_book(u1.id, b1.isbn)
    catalog.get_subscribers_of_the_book(b2.isbn)
    # catalog.user_return_book(u1.id, b2.isbn)
    # catalog.get_notifications_for_reserved_books(u2.id)
    print(catalog.get_total_fine(u1.id))
    # catalog.user_checkout_book(u1.id, b1.isbn)
    print(catalog.get_fine_for_overdue_book_of_the_user(u1.id, b1.isbn))
    books = catalog.get_overdue_books_of_the_user(u1.id)
    print(books)
