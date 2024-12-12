# debug_scripts/find.py 

"""
This script searches for a specific ID across all tables in the GPT_conversations_database.db
and provides all related data.
"""

import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('GPT_conversations_database.db')
conn.row_factory = sqlite3.Row  # Ensure rows behave like dictionaries
cursor = conn.cursor()

# Specify the target ID to search for
target_id = 'insert-here'  # Replace this with the actual ID to search

# Get a list of all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [table[0] for table in cursor.fetchall()]

# Create a list to store data related to the target ID
related_data = []

# Search each table for the target ID
for table_name in tables:
    # Retrieve the schema for the current table to get column names
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [column[1] for column in cursor.fetchall()]

    # Query each column for the target ID
    for column in columns:
        try:
            cursor.execute(f"SELECT * FROM {table_name} WHERE {column} = ?", (target_id,))
            rows = cursor.fetchall()
            for row in rows:
                related_data.append({
                    "Table": table_name,
                    "Column": column,
                    "Row Data": dict(row)  # Convert Row object to dictionary for display
                })
        except sqlite3.OperationalError as e:
            # Handle invalid queries (e.g., incompatible column types)
            print(f"Error querying {table_name}.{column}: {e}")
            continue

# Display all related data
if related_data:
    related_df = pd.DataFrame(related_data)
    print("\nData Related to Target ID:")
    print(related_df)
else:
    print(f"No data found for ID {target_id}")

# Close the database connection
conn.close()
