import mysql.connector
from mysql.connector import Error

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='smart123',  
            database='bank_system'
        )
        if connection.is_connected():
            print("Connected to the database")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def add_customers(customers):
    connection = connect_to_db()
    if connection is None:
        print("Failed to connect to the database.")
        return

    try:
        cursor = connection.cursor()
        query = """
            INSERT IGNORE INTO Customer (name, email, phone_number, address, date_of_birth)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.executemany(query, customers)
        connection.commit()
        print(f"{cursor.rowcount} customers added successfully (duplicates ignored).")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

def transfer_funds(sender_account_id, receiver_account_id, amount):
    connection = connect_to_db()
    if connection is None:
        print("Failed to connect to the database.")
        return

    try:
        cursor = connection.cursor()
        
        # Begin transaction
        connection.start_transaction()

        # Check sender's balance
        cursor.execute("SELECT balance FROM account WHERE account_id = %s", (sender_account_id,))
        sender_balance = cursor.fetchone()
        
        if sender_balance is None:
            raise Exception("Sender account not found.")
        elif sender_balance[0] < amount:
            raise Exception("Insufficient balance in the sender's account.")

        # Deduct amount from sender's account
        cursor.execute(
            "UPDATE account SET balance = balance - %s WHERE account_id = %s",
            (amount, sender_account_id)
        )

        # Add amount to receiver's account
        cursor.execute(
            "UPDATE account SET balance = balance + %s WHERE account_id = %s",
            (amount, receiver_account_id)
        )

        # Commit the transaction
        connection.commit()
        print("Transaction successful!")

    except Exception as e:
        # Rollback in case of any error
        connection.rollback()
        print(f"Transaction failed: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

# Customer data to insert
customers_data = [
    ("Alice Johnson", "alice@example.com", "9876543210", "123 Street, New York", "1990-05-15"),
    ("Bob Smith", "bob@example.com", "9876543211", "456 Avenue, Los Angeles", "1985-08-20"),
    ("Charlie Davis", "charlie@example.com", "9876543212", "789 Boulevard, Chicago", "1992-12-25"),
    ("Diana Prince", "diana@example.com", "9876543213", "1011 Lane, Houston", "1995-03-10"),
    ("Ethan Hunt", "ethan@example.com", "9876543214", "1500 Spy Street, Miami", "1983-07-01"),
    ("Fiona Gallagher", "fiona@example.com", "9876543215", "233 River Road, Boston", "1997-11-22"),
    ("George Orwell", "george@example.com", "9876543216", "600 Liberty Ave, Seattle", "1984-06-25"),
    ("Hannah Montana", "hannah@example.com", "9876543217", "910 Star Blvd, Nashville", "2000-09-02"),
    ("Ian Wright", "ian@example.com", "9876543218", "777 Sports St, Denver", "1988-05-30"),
    ("Alice Johnson", "alice@example.com", "9876543210", "123 Street, New York", "1990-05-15")  # Duplicate
]

# Insert customers
add_customers(customers_data)

# Example transaction: Transfer 500 units from account 1 to account 2
transfer_funds(1, 2, 500.00)
