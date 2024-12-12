# debug_scripts/add_timestamp.py 

import sqlite3

def add_timestamp_column():
    conn = sqlite3.connect('GPT_conversations_database.db')
    cursor = conn.cursor()

    # Step 1: Add the `timestamp` column if it doesn't already exist
    try:
        cursor.execute("ALTER TABLE Conversations ADD COLUMN timestamp TEXT")
        print("Added 'timestamp' column to 'Conversations'.")
    except sqlite3.OperationalError as e:
        print(f"Error adding column: {e}")

    # Step 2: Populate the `timestamp` column using `create_time`
    try:
        cursor.execute("UPDATE Conversations SET timestamp = create_time WHERE timestamp IS NULL")
        print("Populated 'timestamp' column with 'create_time' values.")
    except sqlite3.OperationalError as e:
        print(f"Error populating column: {e}")

    conn.commit()
    conn.close()
    print("Migration completed successfully.")

# Run the script
if __name__ == "__main__":
    add_timestamp_column()
