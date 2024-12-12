# debug_scripts/link_orphan_db.py

import sqlite3
import difflib

# Connect to the database
conn = sqlite3.connect('GPT_conversations_database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def link_orphaned_messages():
    # Identify orphaned messages
    orphaned_messages = cursor.execute(
        "SELECT message_id, content, create_time FROM Messages WHERE conversation_id IS NULL"
    ).fetchall()

    link_log = []

    for message in orphaned_messages:
        message_id = message["message_id"]
        content = message["content"]
        create_time = message["create_time"]

        # Match by timestamp
        matched_conversation = cursor.execute(
            """
            SELECT conversation_id 
            FROM Conversations 
            WHERE ABS(Conversations.create_time - ?) < 600
            ORDER BY ABS(Conversations.create_time - ?) ASC
            LIMIT 1
            """,
            (create_time, create_time)
        ).fetchone()

        if matched_conversation:
            # Update message with matched conversation_id
            cursor.execute(
                "UPDATE Messages SET conversation_id = ? WHERE message_id = ?",
                (matched_conversation["conversation_id"], message_id)
            )
            link_log.append(f"Linked Message ID {message_id} to Conversation ID {matched_conversation['conversation_id']}")
        else:
            # Fallback: Match by content similarity
            potential_matches = cursor.execute("SELECT conversation_id, title FROM Conversations").fetchall()

            best_match_id = None
            highest_similarity = 0

            for conversation in potential_matches:
                similarity = difflib.SequenceMatcher(None, content, conversation["title"]).ratio()
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match_id = conversation["conversation_id"]

            if highest_similarity > 0.6:  # Threshold for similarity
                cursor.execute(
                    "UPDATE Messages SET conversation_id = ? WHERE message_id = ?",
                    (best_match_id, message_id)
                )
                link_log.append(f"Content-linked Message ID {message_id} to Conversation ID {best_match_id} with similarity {highest_similarity:.2f}")

    # Commit changes
    conn.commit()

    # Display results
    for log in link_log:
        print(log)

# Run the script
link_orphaned_messages()

# Verify remaining orphans
remaining_orphans = cursor.execute(
    "SELECT message_id FROM Messages WHERE conversation_id IS NULL"
).fetchall()

if remaining_orphans:
    print("Remaining orphaned messages:", [row["message_id"] for row in remaining_orphans])
else:
    print("All orphaned messages have been successfully linked.")

conn.close()
