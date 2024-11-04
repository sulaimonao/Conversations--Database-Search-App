import os
import json
import sqlite3

# Define database file
db_file = 'ChatGPT_data.db'

# Define folders to scan for JSON files
folders = [
    '/path/to/your/folder'  # Update this to the actual folder path containing JSON files
]

# Connect to SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Create table structure based on your schema
cursor.execute('''CREATE TABLE IF NOT EXISTS Users (user_id TEXT PRIMARY KEY, user_data TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Conversations (conversation_id TEXT PRIMARY KEY, user_id TEXT, timestamp TEXT, conversation_data TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Messages (message_id TEXT PRIMARY KEY, conversation_id TEXT, content TEXT, timestamp TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Feedback (feedback_id TEXT PRIMARY KEY, message_id TEXT, feedback_type TEXT, feedback_content TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS ModelComparisons (comparison_id TEXT PRIMARY KEY, message_id TEXT, model_name TEXT, response_time TEXT, comparison_data TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS SharedConversations (shared_conversation_id TEXT PRIMARY KEY, conversation_id TEXT)''')

# Function to insert data into the respective tables
def insert_into_table(table, data):
    placeholders = ', '.join(['?'] * len(data))
    columns = ', '.join(data.keys())
    sql = f'INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeholders})'
    cursor.execute(sql, list(data.values()))

# Process each JSON file based on file name and insert into appropriate table
for folder in folders:
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Ensure the data is a list (or wrap in a list if it's a single dictionary)
                        if isinstance(data, dict):
                            data = [data]
                        elif not isinstance(data, list):
                            print(f"Unexpected data format in {file_path}: {type(data)}")
                            continue  # Skip files with unexpected format

                        if file == 'conversations.json':
                            for item in data:
                                if isinstance(item, dict):  # Ensure item is a dictionary
                                    conversation_data = {
                                        'conversation_id': item.get('conversation_id'),
                                        'user_id': item.get('user_id'),
                                        'timestamp': item.get('timestamp'),
                                        'conversation_data': json.dumps(item.get('conversation_data'))  # Serialize nested JSON
                                    }
                                    insert_into_table('Conversations', conversation_data)
                                else:
                                    print(f"Unexpected item format in {file_path}: {item}")

                        elif file == 'message_feedback.json':
                            for item in data:
                                if isinstance(item, dict):
                                    feedback_data = {
                                        'feedback_id': item.get('feedback_id'),
                                        'message_id': item.get('message_id'),
                                        'feedback_type': item.get('feedback_type'),
                                        'feedback_content': item.get('feedback_content')
                                    }
                                    insert_into_table('Feedback', feedback_data)
                                else:
                                    print(f"Unexpected item format in {file_path}: {item}")

                        elif file == 'model_comparisons.json':
                            for item in data:
                                if isinstance(item, dict):
                                    model_comparison_data = {
                                        'comparison_id': item.get('comparison_id'),
                                        'message_id': item.get('message_id'),
                                        'model_name': item.get('model_name'),
                                        'response_time': item.get('response_time'),
                                        'comparison_data': json.dumps(item.get('comparison_data'))  # Serialize nested JSON
                                    }
                                    insert_into_table('ModelComparisons', model_comparison_data)
                                else:
                                    print(f"Unexpected item format in {file_path}: {item}")

                        elif file == 'shared_conversations.json':
                            for item in data:
                                if isinstance(item, dict):
                                    shared_conversation_data = {
                                        'shared_conversation_id': item.get('shared_conversation_id'),
                                        'conversation_id': item.get('conversation_id')
                                    }
                                    insert_into_table('SharedConversations', shared_conversation_data)
                                else:
                                    print(f"Unexpected item format in {file_path}: {item}")

                        elif file == 'user.json':
                            for item in data:
                                if isinstance(item, dict):
                                    user_data = {
                                        'user_id': item.get('user_id'),
                                        'user_data': json.dumps(item.get('user_data'))  # Serialize nested JSON if needed
                                    }
                                    insert_into_table('Users', user_data)
                                else:
                                    print(f"Unexpected item format in {file_path}: {item}")

                        elif file == 'messages.json':
                            for item in data:
                                if isinstance(item, dict):
                                    message_data = {
                                        'message_id': item.get('message_id'),
                                        'conversation_id': item.get('conversation_id'),
                                        'content': item.get('content'),
                                        'timestamp': item.get('timestamp')
                                    }
                                    insert_into_table('Messages', message_data)
                                else:
                                    print(f"Unexpected item format in {file_path}: {item}")

                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error reading {file_path}: {e}")

# Commit changes and close database
conn.commit()
conn.close()
print("Database merge completed successfully.")
