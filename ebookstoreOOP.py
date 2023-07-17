from database import Database


def main():
    """
    Main body of the program, displays root menu and calls main functions
    :return: None
    """
    try:
        with Database('ebookstore2.db') as db:

            while True:
                print("\n1. Enter book")
                print("2. Update book")
                print("3. Delete book")
                print("4. Search books")
                print("0. Exit")

                choice = int(input("\nEnter your choice: "))

                if choice == 0:
                    break
                elif choice == 1:
                    db.enter_book()
                elif choice == 2:
                    db.update_book()
                elif choice == 3:
                    db.delete_book()
                elif choice == 4:
                    db.search_books()
                else:
                    print("Invalid choice. Please try again.")

    except Exception as e:
        db.rollback()
        raise e

    finally:
        print("Goodbye!")


if __name__ == "__main__":
    main()
