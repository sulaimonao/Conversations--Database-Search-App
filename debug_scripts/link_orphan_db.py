import sqlite3
import difflib

# Connect to the database
conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row

def link_orphaned_messages():
    # Step 1: Identify orphaned messages (without conversation_id)
    orphaned_messages = conn.execute("""
        SELECT message_id, content, timestamp 
        FROM Messages 
        WHERE conversation_id IS NULL
    """).fetchall()

    # Logging for updates
    link_log = []

    for message in orphaned_messages:
        # Step 2: Match based on timestamp proximity
        matched_conversation = conn.execute("""
            SELECT conversation_id 
            FROM Conversations 
            WHERE ABS(Conversations.timestamp - ?) < 600
            ORDER BY ABS(Conversations.timestamp - ?) ASC
            LIMIT 1
        """, (message['timestamp'], message['timestamp'])).fetchone()
        
        if matched_conversation:
            # Update message with found conversation_id
            conn.execute("""
                UPDATE Messages 
                SET conversation_id = ? 
                WHERE message_id = ?
            """, (matched_conversation['conversation_id'], message['message_id']))
            link_log.append(f"Linked Message ID {message['message_id']} to Conversation ID {matched_conversation['conversation_id']}")
        
        else:
            # Step 3: Content-based matching (if no timestamp match found)
            potential_matches = conn.execute("""
                SELECT conversation_id, conversation_data 
                FROM Conversations
            """).fetchall()

            highest_similarity = 0
            best_match_id = None
            
            # Find best content match
            for conversation in potential_matches:
                conversation_text = conversation['conversation_data']
                similarity_ratio = difflib.SequenceMatcher(None, message['content'], conversation_text).ratio()
                
                if similarity_ratio > highest_similarity:
                    highest_similarity = similarity_ratio
                    best_match_id = conversation['conversation_id']

            # If content similarity is high enough, link the message
            if highest_similarity > 0.6:  # Set a threshold for linking, e.g., 60% similarity
                conn.execute("""
                    UPDATE Messages 
                    SET conversation_id = ? 
                    WHERE message_id = ?
                """, (best_match_id, message['message_id']))
                link_log.append(f"Content-linked Message ID {message['message_id']} to Conversation ID {best_match_id} with {highest_similarity:.2f} similarity.")

    # Commit changes
    conn.commit()

    # Display or log results
    for log_entry in link_log:
        print(log_entry)

# Run the orphaned message linker
link_orphaned_messages()

remaining_orphans = conn.execute("""
    SELECT message_id 
    FROM Messages 
    WHERE conversation_id IS NULL
""").fetchall()

if remaining_orphans:
    print("Remaining orphaned messages found:", remaining_orphans)
else:
    print("All orphaned messages have been successfully linked.")

linked_messages = conn.execute("""
    SELECT message_id, conversation_id, timestamp, content 
    FROM Messages 
    WHERE conversation_id IS NOT NULL
    ORDER BY conversation_id, timestamp
""").fetchall()

print("Successfully Linked Messages:")
for msg in linked_messages:
    print(f"Message ID: {msg['message_id']}, Conversation ID: {msg['conversation_id']}, Timestamp: {msg['timestamp']}")

# Close the connection after use
conn.close()
