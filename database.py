import sqlite3
import os
from tabulate import tabulate


# I have defined a number of methods as staticmethod, so they don't rely on or modify any
# instance-specific attributes or methods, and I can use them without passing the self parameter.
class Database:
    """
    Class representing a database.

    Attributes:
        db_name (str): Database's name.
    """

    def __init__(self, db_name):
        self.db_path = os.path.join(os.getcwd(), db_name)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_table_and_insert_initial_data()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        """
        Use self.conn.rollback() instead of self.rollback()
        :return: None
        """
        self.conn.rollback()

    def create_table_and_insert_initial_data(self):
        """
        Creates the table books if it hasn't been created and populates it with 10 starting records
        :return: None
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            title TEXT, 
            author TEXT, 
            qty INTEGER)
        ''')

        # Check if the table is empty to verify its existence so,
        # it doesn't duplicate the data when inserted for the first time
        self.cursor.execute('''SELECT COUNT(*) FROM books''')
        row_count = self.cursor.fetchone()[0]

        if row_count == 0:
            # I added a dummy record so the 1st proper record
            # in the table starts with id 3001
            self.cursor.execute('''INSERT INTO books(id, title, author, qty) VALUES (3000, 'dummy', 'dummy', 0)''')
            self.cursor.execute('''DELETE FROM books WHERE id=3000''')

            initial_data = [
                ("A Tale of Two Cities", "Charles Dickens", 30),
                ("Harry Potter and the Philosopher's Stone", "J.K. Rowling", 40),
                ("The Lion, the Witch and the Wardrobe", "C. S. Lewis", 25),
                ("The Lord of the Rings", "J.R.R Tolkien", 37),
                ("Alice in Wonderland", "Lewis Carroll", 12),
                ("Oliver Twist", "Charles Dickens", 50),
                ("Great Expectations", "Charles Dickens", 25),
                ("David Copperfield", "Charles Dickens", 35),
                ("The Pickwick Papers", "Charles Dickens", 26),
                ("Harry Potter and the Chamber of Secrets", "J.K. Rowling", 100),
            ]

            self.cursor.executemany('''INSERT INTO books(title, author, qty) VALUES (?, ?, ?)''', initial_data)
            self.commit()

    def enter_book(self):
        """
        Adds a new record to the existing database with book's title, author, and quantity.
        :return: None
        """
        book_data = self.get_book_data()
        if not book_data:
            return

        title, author, qty = book_data
        existing_title = self.check_existing_title(title)

        if existing_title:
            if not self.confirm_insertion(title):
                print("Book insertion cancelled.")
                return

        self.insert_book(title, author, qty)
        print(f"Book '{title}' by {author} has been added successfully.")

    @staticmethod
    def get_book_data():
        """
        Fetch the properties of the record or book
        :return: title, author, qty
        """
        try:
            title = input("Enter the book title: ")
            author = input("Enter the book author: ")
            qty = int(input("Enter the quantity: "))
            return title, author, qty
        except ValueError:
            print("Invalid input. Please enter the correct data type.")
            return None

    def check_existing_title(self, title):
        """
        Fetch the title for a specific record or book
        :param title:
        :return: Single book's title
        """
        self.cursor.execute('''SELECT title FROM books WHERE title = ?''', (title,))
        return self.cursor.fetchone()

    @staticmethod
    def confirm_insertion(title):
        """
        Checks if the user is happy to proceed with the insertion of a duplicated book
        :param title:
        :return: proceed
        """
        print(f"Warning: A book with the title '{title}' already exists in the database.")
        proceed = input("Do you want to continue with the insertion? (y/n): ").lower()
        return proceed == 'y'

    def insert_book(self, title, author, qty):
        """
        Adds a new record or book to the database with the parameters title, author and qty
        :param title:
        :param author:
        :param qty:
        :return: None
        """
        self.cursor.execute('''INSERT INTO books(title, author, qty) VALUES (?, ?, ?)''', (title, author, qty))
        self.commit()

    def update_book(self):
        """
        Update an existing book's title, author, and quantity in the database.
        :return: None
        """
        book_id = self.get_book_id()
        if not book_id:
            return

        result = self.get_book_by_id(book_id)
        if not result:
            print("No book found with the given ID.")
            return

        print("\nCurrent book information:")
        self.display_results([result])  # Wrap result in a list to pass to display_results

        new_title, new_author, new_qty = self.get_updated_book_data(result)

        self.update_book_in_db(book_id, new_title, new_author, new_qty)
        print(f"Book with ID {book_id} has been updated successfully.")

    @staticmethod
    def get_book_id():
        """
        Get the book ID from the user.
        :return: int or None
        """
        try:
            return int(input("Enter the book ID to update: "))
        except ValueError:
            print("Invalid input. Please enter the correct data type.")
            return None

    def get_book_by_id(self, book_id):
        """
        Fetch a book by ID from the database.
        :param book_id: int
        :return: tuple or None
        """
        self.cursor.execute('''SELECT * FROM books WHERE id=?''', (book_id,))
        return self.cursor.fetchone()

    @staticmethod
    def get_updated_book_data(current_data):
        """
        Get the updated book data from the user.
        :param current_data: tuple
        :return: tuple
        """
        title, author, qty = current_data[1], current_data[2], current_data[3]

        new_title = input("\nEnter the new book title or leave empty to keep the current title: ") or title
        new_author = input("Enter the new author or leave empty to keep the current author: ") or author

        try:
            new_qty = input("Enter the new quantity or leave empty to keep the current quantity: ")
            new_qty = int(new_qty) if new_qty else qty
        except ValueError:
            print("Invalid input. Please enter the correct data type.")
            return None

        return new_title, new_author, new_qty

    def update_book_in_db(self, book_id, title, author, qty):
        """
        Update the book in the database with the new data.
        :param book_id: int
        :param title: str
        :param author: str
        :param qty: int
        :return: None
        """
        self.cursor.execute('''UPDATE books SET title=?, author=?, qty=? WHERE id=?''', (title, author, qty, book_id))
        self.commit()

    def delete_book(self):
        """
        Deletes a single row using the specific ID provided by the user
        :return: None
        """
        book_id = int(input("Enter the book ID to delete: "))
        self.cursor.execute('''DELETE FROM books WHERE id = ?''', (book_id,))
        self.commit()
        print("Book deleted successfully.")

    @staticmethod
    def display_results(results):
        """
        Displays records using tabulate module
        :param results:
        :return:
        """
        headers = ['ID', 'Title', 'Author', 'Quantity']  # Define headers once for all options
        print("\nSearch result:")
        print(tabulate(results, headers=headers, tablefmt='fancy_grid'))

    def search_books(self):
        """
        Displays main menu for search option and calls the correspondent functions
        :return: None
        """
        while True:
            print("\nSearch books by:")
            print("1. ID")
            print("2. Title")
            print("3. Author")
            print("4. Display all books")
            print("0. Return to main menu")

            try:
                option = int(input("\nEnter your choice: "))
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            if option == 0:
                break
            elif option == 1:
                self.search_by_id()
            elif option == 2:
                self.search_by_title()
            elif option == 3:
                self.search_by_author()
            elif option == 4:
                self.display_all_books()
            else:
                print("Invalid choice. Please try again.")

    def display_all_books(self):
        """
        Displays all records in the database
        :return: None
        """
        print("\nFull inventory:")
        self.cursor.execute('''SELECT id, title, author, qty FROM books''')
        results = self.cursor.fetchall()
        self.display_results(results)

    def search_by_id(self):
        """
        Fetch one record in the database by ID
        :return: None
        """
        search_id = int(input("Enter the book ID: "))
        self.cursor.execute('''SELECT id, title, author, qty FROM books WHERE id = ?''', (search_id,))
        result = self.cursor.fetchone()
        if result:
            self.display_results([result])  # Wrap result in a list to pass to display_results
        else:
            print("No books found with the given ID.")

    def search_by_title(self):
        """
        Fetch one or more records in the database by title
        :return: None
        """
        search_title = input("Enter the book title: ")
        self.cursor.execute('''SELECT id, title, author, qty FROM books WHERE title LIKE ?''', (f"%{search_title}%",))
        results = self.cursor.fetchall()
        if results:
            self.display_results(results)
        else:
            print("No books found with the given title.")

    def search_by_author(self):
        """
        Fetch all records in the database by author
        :return: None
        """
        search_author = input("Enter the author's name: ")
        self.cursor.execute('''SELECT id, title, author, qty FROM books WHERE author LIKE ?''', (f"%{search_author}%",))
        results = self.cursor.fetchall()
        if results:
            self.display_results(results)
        else:
            print("No books found with the given author.")
