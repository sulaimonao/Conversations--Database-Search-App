import os
import json
import sqlite3

# Define database file
db_file = 'ChatGPT_data.db'

# Define folders to scan for JSON files
folders = [
    '//ChatGPT_data/adhdauhd', #you extracted chatgpt user folder path goes here
    # Add more folders as needed
]

# Connect to SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Create table structure
cursor.execute('''
    CREATE TABLE IF NOT EXISTS data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT,
        file_path TEXT,
        last_modified TEXT,
        category TEXT,
        tags TEXT,
        summary TEXT,
        content TEXT,
        code TEXT,
        UNIQUE(file_path)
    )
''')

# Function to insert data into the database
def insert_data(data):
    cursor.execute('''
        INSERT OR IGNORE INTO data (file_name, file_path, last_modified, category, tags, summary, content, code)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("file_name"),
        data.get("file_path"),
        data.get("last_modified"),
        data.get("category"),
        ','.join(data.get("tags", [])),
        data.get("summary"),
        data.get("content"),
        data.get("code")
    ))

# Traverse folders and read JSON files
for folder in folders:
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                        # Ensure json_data is a list of dictionaries
                        if isinstance(json_data, list):
                            for item in json_data:
                                insert_data(item)
                        else:
                            insert_data(json_data)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error reading {file_path}: {e}")

# Commit changes and close database
conn.commit()
conn.close()
print("Database merge completed successfully.")
