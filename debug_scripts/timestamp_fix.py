# debug_scripts/timestamp_fix.py

import sqlite3
import json

def update_timestamp_with_create_time():
    conn = sqlite3.connect('GPT_conversations_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT conversation_id, create_time FROM Conversations WHERE timestamp IS NULL")
    records = cursor.fetchall()

    for record in records:
        conversation_id = record["conversation_id"]
        create_time = record["create_time"]

        if create_time:
            cursor.execute(
                "UPDATE Conversations SET timestamp = ? WHERE conversation_id = ?",
                (create_time, conversation_id)
            )

    conn.commit()
    conn.close()
    print("Timestamp update complete.")

# Run the update
update_timestamp_with_create_time()
