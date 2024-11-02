import sqlite3
import json

def update_timestamp_with_create_time():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT conversation_id, conversation_data FROM Conversations WHERE timestamp IS NULL")
    records = cursor.fetchall()

    for record in records:
        conversation_id, conversation_data = record
        try:
            # Parse JSON to get create_time
            data = json.loads(conversation_data)
            create_time = data.get("create_time")
            
            if create_time:
                # Update the timestamp with create_time
                cursor.execute(
                    "UPDATE Conversations SET timestamp = ? WHERE conversation_id = ?",
                    (create_time, conversation_id)
                )
        except json.JSONDecodeError:
            print(f"Error decoding JSON for conversation_id: {conversation_id}")
        except Exception as e:
            print(f"Unexpected error for conversation_id {conversation_id}: {e}")

    conn.commit()
    conn.close()
    print("Timestamp update complete.")

# Run the update
update_timestamp_with_create_time()
