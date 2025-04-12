import os
import sqlite3

# Database file
DATABASE_FILE = "library.db"

# Initialize the database and create table if not exists
def initialize_database():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS books
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  author TEXT NOT NULL,
                  year INTEGER NOT NULL,
                  genre TEXT NOT NULL,
                  read_status INTEGER NOT NULL)''')
    conn.commit()
    conn.close()

def add_book():
    """Add a book to the library."""
    print("\n📖 Add a Book")
    title = input("Enter the book title: ")
    author = input("Enter the author's name: ")
    year = int(input("Enter the publication year: "))
    genre = input("Enter the genre: ")
    read_status = input("Have you read this book? (Yes/No): ").strip().lower() == "yes"
    
    if title and author and genre:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO books (title, author, year, genre, read_status) VALUES (?, ?, ?, ?, ?)",
                  (title, author, year, genre, read_status))
        conn.commit()
        conn.close()
        print("✅ Book added successfully!")
    else:
        print("❌ Please fill in all fields.")

def remove_book():
    """Remove a book from the library by title."""
    print("\n❌ Remove a Book")
    title = input("Enter the title of the book to remove: ")
    
    if title:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM books WHERE title = ?", (title,))
        conn.commit()
        conn.close()
        print(f"✅ '{title}' removed successfully!")
    else:
        print("❌ Please enter a title.")

def search_book():
    """Search for a book by title or author."""
    print("\n🔍 Search for a Book")
    search_by = input("Search by (Title/Author): ").strip().lower()
    search_term = input(f"Enter the {search_by}: ").strip().lower()
    
    if search_term:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        if search_by == "title":
            c.execute("SELECT * FROM books WHERE title LIKE ?", ('%' + search_term + '%',))
        elif search_by == "author":
            c.execute("SELECT * FROM books WHERE author LIKE ?", ('%' + search_term + '%',))
        matching_books = c.fetchall()
        conn.close()
        
        if matching_books:
            print("📚 Matching Books:")
            for i, book in enumerate(matching_books, start=1):
                status = "✅ Read" if book[5] else "❌ Unread"
                print(f"{i}. **{book[1]}** by {book[2]} ({book[3]}) - {book[4]} - {status}")
        else:
            print("❌ No matching books found.")
    else:
        print("❌ Please enter a search term.")

def display_all_books():
    """Display all books in the library."""
    print("\n📚 Your Library")
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM books")
    books = c.fetchall()
    conn.close()
    
    if not books:
        print("No books in the library.")
        return
    
    for i, book in enumerate(books, start=1):
        status = "✅ Read" if book[5] else "❌ Unread"
        print(f"{i}. **{book[1]}** by {book[2]} ({book[3]}) - {book[4]} - {status}")

def display_statistics():
    """Display library statistics."""
    print("\n📊 Library Statistics")
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM books")
    total_books = c.fetchone()[0]
    
    if total_books == 0:
        print("No books in the library.")
        return
    
    c.execute("SELECT COUNT(*) FROM books WHERE read_status = 1")
    read_books = c.fetchone()[0]
    percentage_read = (read_books / total_books) * 100
    
    print(f"📖 **Total books:** {total_books}")
    print(f"📈 **Percentage read:** {percentage_read:.1f}%")
    conn.close()

def main():
    """Main function to run the console-based app."""
    print("📚 Personal Library Manager")
    print("Welcome to your personal library! Manage your book collection with ease.")
    
    # Initialize database at startup
    initialize_database()
    
    while True:
        print("\nMenu:")
        print("1. Add a Book")
        print("2. Remove a Book")
        print("3. Search for a Book")
        print("4. Display All Books")
        print("5. Display Statistics")
        print("6. Exit")
        
        choice = input("Choose an option (1-6): ").strip()
        
        if choice == "1":
            add_book()
        elif choice == "2":
            remove_book()
        elif choice == "3":
            search_book()
        elif choice == "4":
            display_all_books()
        elif choice == "5":
            display_statistics()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
