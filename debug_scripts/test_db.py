# debug_scripts/test_db.py 

import sqlite3
import pandas as pd

# Connect to the database
db_path = "GPT_conversations_database.db"  # Replace with your database path
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def check_table_schema():
    """Print schema for all tables."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]

    print("\nDatabase Schema:")
    for table in tables:
        print(f"\nTable: {table}")
        cursor.execute(f"PRAGMA table_info({table});")
        schema = cursor.fetchall()
        for column in schema:
            print(f"  {column[1]} ({column[2]})")

def sample_data(table_name, limit=5):
    """Print sample data from a table."""
    print(f"\nSample Data from {table_name}:")
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
    rows = cursor.fetchall()
    if rows:
        df = pd.DataFrame([dict(row) for row in rows])
        print(df)
    else:
        print("  No data found.")

def check_null_values(table_name, column_name):
    """Check for null values in a specific column."""
    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NULL;")
    count = cursor.fetchone()[0]
    print(f"\n{table_name}.{column_name}: {count} null values found.")

def main():
    # Check schema
    check_table_schema()

    # Check for required columns and their null values
    required_checks = [
        ("Conversations", "timestamp"),
        ("Messages", "conversation_id"),
        ("Messages", "content"),
    ]

    for table, column in required_checks:
        try:
            check_null_values(table, column)
        except sqlite3.OperationalError:
            print(f"\nError: Column {column} does not exist in table {table}.")

    # Display sample data
    tables_to_sample = ["Conversations", "Messages"]
    for table in tables_to_sample:
        sample_data(table)

if __name__ == "__main__":
    main()

# Close the connection
conn.close()
