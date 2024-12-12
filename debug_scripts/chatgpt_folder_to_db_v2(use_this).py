import os
import json
import pandas as pd
import sqlite3

def flatten_json(json_data, data_type):
    """Flatten JSON data based on its type."""
    if data_type == "conversations":
        flattened_data = []
        for conv in json_data:
            conversation_id = conv.get("conversation_id")
            title = conv.get("title")
            create_time = conv.get("create_time")
            update_time = conv.get("update_time")
            mapping = conv.get("mapping", {})
            for msg_id, msg in mapping.items():
                message = msg.get("message", {})
                flattened_data.append({
                    "conversation_id": conversation_id,
                    "message_id": message.get("id"),
                    "author_role": message.get("author", {}).get("role"),
                    "content": message.get("content", {}).get("parts", [None])[0],
                    "create_time": message.get("create_time"),
                    "update_time": message.get("update_time"),
                    "status": message.get("status"),
                    "parent_id": msg.get("parent"),
                })
        return pd.DataFrame(flattened_data)

    elif data_type == "model_comparisons":
        flattened_data = []
        for item in json_data:
            flattened_data.append({
                "comparison_id": item.get("comparison_id"),
                "conversation_id": item.get("conversation_id"),
                "criteria": item.get("criteria"),
                "results": item.get("results"),
            })
        return pd.DataFrame(flattened_data)

    elif data_type == "message_feedback":
        flattened_data = []
        for feedback in json_data:
            flattened_data.append({
                "feedback_id": feedback.get("feedback_id"),
                "message_id": feedback.get("message_id"),
                "feedback_type": feedback.get("type"),
                "feedback_content": feedback.get("content"),
            })
        return pd.DataFrame(flattened_data)

def save_to_database(flattened_dataframes, db_path):
    """Save flattened dataframes to SQLite database with deduplication."""
    conn = sqlite3.connect(db_path)

    # Define the schema
    schema = {
        "Conversations": [
            ("conversation_id", "TEXT PRIMARY KEY"),
            ("title", "TEXT"),
            ("create_time", "TEXT"),
            ("update_time", "TEXT"),
        ],
        "Messages": [
            ("message_id", "TEXT PRIMARY KEY"),
            ("conversation_id", "TEXT"),
            ("parent_id", "TEXT"),
            ("author_role", "TEXT"),
            ("content", "TEXT"),
            ("create_time", "TEXT"),
            ("update_time", "TEXT"),
            ("status", "TEXT"),
        ],
        "ModelComparisons": [
            ("comparison_id", "TEXT PRIMARY KEY"),
            ("conversation_id", "TEXT"),
            ("criteria", "TEXT"),
            ("results", "TEXT"),
        ],
        "MessageFeedback": [
            ("feedback_id", "TEXT PRIMARY KEY"),
            ("message_id", "TEXT"),
            ("feedback_type", "TEXT"),
            ("feedback_content", "TEXT"),
        ],
    }

    # Create tables
    for table, columns in schema.items():
        column_definitions = ", ".join(f"{col} {dtype}" for col, dtype in columns)
        conn.execute(f"CREATE TABLE IF NOT EXISTS {table} ({column_definitions})")

    # Insert data with deduplication
    for table, dataframe in flattened_dataframes.items():
        placeholders = ", ".join("?" for _ in dataframe.columns)
        column_names = ", ".join(dataframe.columns)
        insert_query = f"INSERT OR IGNORE INTO {table} ({column_names}) VALUES ({placeholders})"
        conn.executemany(insert_query, dataframe.to_records(index=False))

    conn.commit()
    conn.close()

def process_folders(folder_paths, db_path):
    """Process all JSON files across multiple folders and save to database."""
    json_files = ["conversations.json", "model_comparisons.json", "message_feedback.json"]

    for folder_path in folder_paths:
        print(f"Processing folder: {folder_path}")
        flattened_dataframes = {}

        for file_name in json_files:
            file_path = os.path.join(folder_path, file_name)
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    json_data = json.load(f)
                data_type = file_name.split(".")[0]  # Infer data type from file name
                flattened_dataframes[data_type] = flatten_json(json_data, data_type)

        # Save the dataframes to the database
        save_to_database(flattened_dataframes, db_path)

# Example usage
folders = [
    "path/to/folder1",
    "path/to/folder2",
    "path/to/folder3",
]
db_path = "output_database.db"
process_folders(folders, db_path)
