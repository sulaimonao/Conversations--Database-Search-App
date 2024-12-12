# app/parsers.py

import json
import sqlite3
from .utils import format_timestamp
from .helpers import fetch_feedback, fetch_model_comparisons

def parse_conversation_data(conversation_row, conn):
    try:
        # Validate input
        if not isinstance(conversation_row, sqlite3.Row):
            raise TypeError(f"Expected sqlite3.Row, got {type(conversation_row)}")

        # Extract fields
        conversation_id = conversation_row["conversation_id"]
        title = conversation_row["title"] or "No Title"
        create_time = format_timestamp(conversation_row["create_time"])
        update_time = format_timestamp(conversation_row["update_time"])

        print(f"Parsing messages for conversation_id: {conversation_id}")
        # Fetch messages
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Messages WHERE conversation_id = ? ORDER BY create_time ASC",
            (conversation_id,)
        )
        message_rows = cursor.fetchall()

        messages = [
            {
                "message_id": msg["message_id"],
                "author_role": msg["author_role"] or "unknown",
                "content": msg["content"] or "No content available",
                "timestamp": format_timestamp(msg["create_time"]),
                "status": msg["status"],
            }
            for msg in message_rows
        ]

        return {
            "conversation_id": conversation_id,
            "title": title,
            "create_time": create_time,
            "update_time": update_time,
            "messages": messages,
        }

    except Exception as e:
        print(f"Error parsing conversation data: {e}")
        return {
            "conversation_id": "unknown",
            "title": "Error",
            "create_time": "N/A",
            "update_time": "N/A",
            "messages": [],
        }
