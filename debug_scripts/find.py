"""
This script searches for a specific ID across all tables in the database.db
and provides all related data. place in project root
"""

import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Specify the target ID to search for
target_id = 'insert-here'

# Get a list of all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Create a list to store data related to the target ID
related_data = []

# Search each table for the target ID
for table in tables:
    table_name = table[0]
    
    # Retrieve the schema for the current table to get column names
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    # Query the table to check for the target ID in each column
    for column_name in column_names:
        # Execute a query to search for the target ID in the current column
        try:
            cursor.execute(f"SELECT * FROM {table_name} WHERE {column_name} = ?;", (target_id,))
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    related_data.append({
                        "Table": table_name,
                        "Column": column_name,
                        "Row Data": row
                    })
        except sqlite3.OperationalError:
            # Ignore columns where the operation is not possible (e.g., incompatible data types)
            continue

# Display all related data in a DataFrame
if related_data:
    related_df = pd.DataFrame(related_data)
    print("\nData Related to Target ID:")
    print(related_df)
else:
    print(f"No data found for ID {target_id}")

# Adjust pandas display options to show full content
pd.set_option('display.max_colwidth', None)
print(related_df)


# Close the database connection
conn.close()
