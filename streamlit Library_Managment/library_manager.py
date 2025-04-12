import streamlit as st
import sqlite3
import pandas as pd
import base64
from PIL import Image
import io
import hashlib

# Database file
DATABASE_FILE = "library.db"

# Initialize the database and create tables if they don't exist
def initialize_database():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    
    # Books table
    c.execute('''CREATE TABLE IF NOT EXISTS books
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  author TEXT NOT NULL,
                  year INTEGER NOT NULL,
                  genre TEXT NOT NULL,
                  read_status INTEGER NOT NULL,
                  rating INTEGER,
                  review TEXT,
                  cover_image BLOB,
                  user_id INTEGER)''')
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL UNIQUE,
                  password TEXT NOT NULL)''')
    
    conn.commit()
    conn.close()

# Update the table schema to add the user_id column if it doesn't exist
def update_table_schema():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    # Check if the user_id column exists
    c.execute("PRAGMA table_info(books)")
    columns = c.fetchall()
    column_names = [column[1] for column in columns]
    if 'user_id' not in column_names:
        c.execute("ALTER TABLE books ADD COLUMN user_id INTEGER")
        conn.commit()
    conn.close()

# Convert image to binary
def image_to_binary(image):
    buf = io.BytesIO()
    image.save(buf, format='JPEG')
    return buf.getvalue()

# Convert binary to image
def binary_to_image(binary):
    return Image.open(io.BytesIO(binary))

# Hash password using hashlib
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Verify password using hashlib
def verify_password(password, hashed):
    return hashlib.sha256(password.encode()).hexdigest() == hashed

# User registration
def register_user(username, password):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

# User login
def login_user(username, password):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if user and verify_password(password, user[1]):
        return user[0]  # Return user ID
    return None

# Add a book to the library
def add_book(user_id):
    st.subheader("📖 Add a Book")
    title = st.text_input("Title")
    author = st.text_input("Author")
    year = st.number_input("Publication Year", min_value=1800, max_value=2100)
    genre = st.text_input("Genre")
    read_status = st.checkbox("Have you read this book?")
    rating = st.slider("Rating (1-5)", 1, 5) if read_status else None
    review = st.text_area("Review") if read_status else None
    cover_image = st.file_uploader("Upload Book Cover (optional)", type=["jpg", "jpeg", "png"])
    
    if st.button("Add Book"):
        if title and author and genre:
            conn = sqlite3.connect(DATABASE_FILE)
            c = conn.cursor()
            cover_binary = image_to_binary(Image.open(cover_image)) if cover_image else None
            c.execute("INSERT INTO books (title, author, year, genre, read_status, rating, review, cover_image, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (title, author, year, genre, read_status, rating, review, cover_binary, user_id))
            conn.commit()
            conn.close()
            st.success("✅ Book added successfully!")
        else:
            st.error("❌ Please fill in all fields.")

# Remove a book from the library by title
def remove_book(user_id):
    st.subheader("❌ Remove a Book")
    title = st.text_input("Enter the title of the book to remove")
    
    if st.button("Remove Book"):
        if title:
            conn = sqlite3.connect(DATABASE_FILE)
            c = conn.cursor()
            c.execute("DELETE FROM books WHERE title = ? AND user_id = ?", (title, user_id))
            conn.commit()
            conn.close()
            st.success(f"✅ '{title}' removed successfully!")
        else:
            st.error("❌ Please enter a title.")

# Search for a book by title or author
def search_book(user_id):
    st.subheader("🔍 Search for a Book")
    search_by = st.radio("Search by", ["Title", "Author"])
    search_term = st.text_input(f"Enter the {search_by}")
    
    if st.button("Search"):
        if search_term:
            conn = sqlite3.connect(DATABASE_FILE)
            c = conn.cursor()
            if search_by == "Title":
                c.execute("SELECT * FROM books WHERE title LIKE ? AND user_id = ?", ('%' + search_term + '%', user_id))
            elif search_by == "Author":
                c.execute("SELECT * FROM books WHERE author LIKE ? AND user_id = ?", ('%' + search_term + '%', user_id))
            matching_books = c.fetchall()
            conn.close()
            
            if matching_books:
                st.write("📚 Matching Books:")
                for book in matching_books:
                    status = "✅ Read" if book[5] else "❌ Unread"
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if book[8]:
                            st.image(binary_to_image(book[8]), width=100)
                    with col2:
                        st.write(f"**{book[1]}** by {book[2]} ({book[3]}) - {book[4]} - {status}")
                        if book[6]:
                            st.write(f"⭐ Rating: {book[6]}/5")
                        if book[7]:
                            st.write(f"📝 Review: {book[7]}")
            else:
                st.error("❌ No matching books found.")
        else:
            st.error("❌ Please enter a search term.")

# Display all books in the library
def display_all_books(user_id):
    st.subheader("📚 Your Library")
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE user_id = ?", (user_id,))
    books = c.fetchall()
    conn.close()
    
    if not books:
        st.write("No books in the library.")
        return
    
    for book in books:
        status = "✅ Read" if book[5] else "❌ Unread"
        col1, col2 = st.columns([1, 4])
        with col1:
            if book[8]:
                st.image(binary_to_image(book[8]), width=100)
        with col2:
            st.write(f"**{book[1]}** by {book[2]} ({book[3]}) - {book[4]} - {status}")
            if book[6]:
                st.write(f"⭐ Rating: {book[6]}/5")
            if book[7]:
                st.write(f"📝 Review: {book[7]}")

# Export library data
def export_data(user_id):
    st.subheader("📤 Export Library Data")
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query("SELECT * FROM books WHERE user_id = ?", conn, params=(user_id,))
    conn.close()
    
    if st.button("Export as CSV"):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="library.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    if st.button("Export as JSON"):
        json = df.to_json(orient='records')
        b64 = base64.b64encode(json.encode()).decode()
        href = f'<a href="data:file/json;base64,{b64}" download="library.json">Download JSON File</a>'
        st.markdown(href, unsafe_allow_html=True)

# Main function to run the Streamlit app
def main():
    st.set_page_config(page_title="Personal Library Manager", page_icon="📚", layout="wide")
    
    # Initialize database at startup
    initialize_database()
    update_table_schema()  # Update the table schema if needed
    
    st.title("📚 Personal Library Manager")
    st.write("Welcome to your personal library! Manage your book collection with ease.")
    
    # User authentication
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    
    if st.session_state.user_id is None:
        st.sidebar.subheader("Login / Register")
        choice = st.sidebar.radio("Choose an option", ["Login", "Register"])
        
        if choice == "Login":
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Login"):
                user_id = login_user(username, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.sidebar.success("Logged in successfully!")
                else:
                    st.sidebar.error("Invalid username or password.")
        
        elif choice == "Register":
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Register"):
                register_user(username, password)
                st.sidebar.success("Registration successful! Please log in.")
    
    else:
        st.sidebar.subheader(f"Logged in as User {st.session_state.user_id}")
        if st.sidebar.button("Logout"):
            st.session_state.user_id = None
            st.sidebar.success("Logged out successfully!")
        
        # Sidebar for navigation
        st.sidebar.title("Menu")
        menu = ["Add a Book", "Remove a Book", "Search for a Book", "Display All Books", "Export Data"]
        choice = st.sidebar.radio("Choose an option", menu)
        
        if choice == "Add a Book":
            add_book(st.session_state.user_id)
        elif choice == "Remove a Book":
            remove_book(st.session_state.user_id)
        elif choice == "Search for a Book":
            search_book(st.session_state.user_id)
        elif choice == "Display All Books":
            display_all_books(st.session_state.user_id)
        elif choice == "Export Data":
            export_data(st.session_state.user_id)

if __name__ == "__main__":
    main()