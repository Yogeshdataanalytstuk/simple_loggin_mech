import sqlite3 as sql
import bcrypt

def create_table():
    """Create user table if it doesn't exist in the 'lprlogin.db' database."""
    with sql.connect("lprlogin.db") as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                ip_address TEXT NOT NULL
            )
        """)
        con.commit()

def insert_user(username, password, ip_address):
    """Insert a new user into the database with the password hashed using bcrypt."""
    # Hashing the password with bcrypt
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        with sql.connect("lprlogin.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO users (username, password, ip_address) VALUES (?, ?, ?)", (username, hashed_password, ip_address))
            con.commit()
            print("User added successfully.")
    except sql.IntegrityError:
        print("Error: Could not insert user. Username may already exist.")
    except sql.Error as e:
        print(f"Database error: {e}")

def retrieve_users():
    """Retrieve all users from the database."""
    try:
        with sql.connect("lprlogin.db") as con:
            cur = con.cursor()
            cur.execute("SELECT username, password, ip_address FROM users")
            users = cur.fetchall()
            return users
    except sql.Error as e:
        print(f"Database error: {e}")
        return []

def get_user_input():
    """Get username, password, and IP address input from the user."""
    username = input("Enter username: ")
    password = input("Enter password: ")
    ip_address = input("Enter IP address: ")
    return username, password, ip_address

def main():
    create_table()  # Ensure the database table is ready
    username, password, ip_address = get_user_input()
    insert_user(username, password, ip_address)  # Insert new user
    users = retrieve_users()  # Retrieve and print all users
    print("Registered users:")
    for user in users:
        print(f"Username: {user[0]}, Password: {user[1].decode()} (hashed), IP Address: {user[2]}")

if __name__ == "__main__":
    main()
