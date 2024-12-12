# app/routes.py

from flask import Blueprint, render_template, request, make_response, jsonify
from .db import get_db_connection
from .utils import format_timestamp, log_search, get_recent_searches
from .parsers import parse_conversation_data
from .helpers import fetch_feedback, fetch_model_comparisons
from datetime import datetime
import math
import logging
from contextlib import closing

main = Blueprint('main', __name__)

@main.route('/')
def index():
    query = request.args.get('query', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    with closing(get_db_connection()) as conn:
        # Base SQL query
        sql_query = "SELECT * FROM Conversations WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM Conversations WHERE 1=1"
        sql_params, count_params = [], []

        # Apply filters
        if query:
            sql_query += " AND title LIKE ?"
            count_query += " AND title LIKE ?"
            sql_params.append(f"%{query}%")
            count_params.append(f"%{query}%")
        if start_date:
            sql_query += " AND datetime(create_time, 'unixepoch') >= ?"
            count_query += " AND datetime(create_time, 'unixepoch') >= ?"
            sql_params.append(start_date)
            count_params.append(start_date)
        if end_date:
            sql_query += " AND datetime(create_time, 'unixepoch') <= ?"
            count_query += " AND datetime(create_time, 'unixepoch') <= ?"
            sql_params.append(end_date)
            count_params.append(end_date)

        # Fetch total count for pagination
        total_records = conn.execute(count_query, count_params).fetchone()[0]
        total_pages = math.ceil(total_records / per_page)

        # Fetch paginated results
        sql_query += " LIMIT ? OFFSET ?"
        sql_params.extend([per_page, offset])
        conversations = conn.execute(sql_query, sql_params).fetchall()

        # Process data for rendering
        results = []
        for conversation in conversations:
            print(f"Processing conversation row: {conversation}")
            print(f"Fetched conversations: {conversations}")
            parsed_data = parse_conversation_data(conversation, conn)  # Pass entire row
            results.append({
                "conversation_id": parsed_data["conversation_id"],
                "title": parsed_data["title"],
                "create_time": parsed_data["create_time"],
                "update_time": parsed_data["update_time"],
                "messages": parsed_data["messages"],
            })

    return render_template(
        'index.html',
        conversations=results,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        query=query,
        start_date=start_date,
        end_date=end_date
    )

@main.route('/conversation/<conversation_id>')
def conversation(conversation_id):
    with closing(get_db_connection()) as conn:
        # Fetch conversation details
        cursor = conn.cursor()
        print(f"Fetching conversation with ID: {conversation_id}")
        cursor.execute("SELECT * FROM Conversations WHERE conversation_id = ?", (conversation_id,))
        conversation_row = cursor.fetchone()
        print(f"Fetched conversation row: {conversation_row}")

        if not conversation_row:
            print(f"Conversation ID {conversation_id} not found.")
            return "Conversation not found", 404

        # Parse conversation data
        parsed_data = parse_conversation_data(conversation_row, conn)
        print(f"Parsed conversation data: {parsed_data}")

    return render_template(
        'conversation.html',
        title=parsed_data["title"],
        create_time=parsed_data["create_time"],
        update_time=parsed_data["update_time"],
        messages=parsed_data["messages"]
    )

@main.route('/review_orphaned_messages')
def review_orphaned_messages():
    with closing(get_db_connection()) as conn:
        orphaned_messages = conn.execute("""
            SELECT * FROM Messages
            WHERE conversation_id IS NULL
        """).fetchall()

        matched_messages = []
        for message in orphaned_messages:
            matched_conversation = find_matching_conversations(message, conn)
            if matched_conversation:
                matched_messages.append({
                    "message_id": message['message_id'],
                    "potential_conversation_id": matched_conversation['conversation_id'],
                    "conversation_title": matched_conversation['title'],
                    "timestamp": message['timestamp'],
                    "user_id": message['user_id']
                })

        return render_template('review_orphaned_messages.html', matched_messages=matched_messages)

# Helper function for finding matching conversations
def find_matching_conversations(message, conn):
    timestamp = message['timestamp']
    user_id = message['user_id']
    
    matched_conversation = conn.execute("""
        SELECT * FROM Conversations
        WHERE user_id = ? AND ABS(timestamp - ?) < 3600
        ORDER BY ABS(timestamp - ?) ASC
        LIMIT 1
    """, (user_id, timestamp)).fetchone()
    
    return matched_conversation

@main.route('/link_orphaned_messages', methods=['POST'])
def link_orphaned_messages():
    with closing(get_db_connection()) as conn:
        orphaned_messages = conn.execute("""
            SELECT * FROM Messages
            WHERE conversation_id IS NULL
        """).fetchall()
        
        for message in orphaned_messages:
            matched_conversation = find_matching_conversations(message, conn)
            if matched_conversation:
                conn.execute("""
                    UPDATE Messages
                    SET conversation_id = ?
                    WHERE message_id = ?
                """, (matched_conversation['conversation_id'], message['message_id']))

        conn.commit()
    return "Orphaned messages have been linked to conversations.", 200

@main.route('/conversation/<conversation_id>/export/json', methods=['POST'])
def export_conversation_json(conversation_id):
    conn = get_db_connection()
    conversation = conn.execute("SELECT * FROM Conversations WHERE conversation_id = ?", (conversation_id,)).fetchone()
    conn.close()

    if conversation:
        # Parse conversation data to ensure nested content is included
        parsed_data = parse_conversation_data(conversation['conversation_data'])
        title = parsed_data.get("title", "No Title")
        create_time = parsed_data.get("create_time", "N/A")
        update_time = parsed_data.get("update_time", "N/A")
        messages = parsed_data.get("messages", [])
        print(f"Type of conversation_row: {type(conversation_row)}, Value: {conversation_row}")


        # Structure JSON for full export
        conversation_json = {
            "conversation_id": conversation['conversation_id'],
            "title": title,
            "create_time": create_time,
            "update_time": update_time,
            "messages": [
                {
                    "message_id": message["message_id"],
                    "author_role": message.get("author_role", "unknown"),
                    "content": message["content"],
                    "timestamp": message["timestamp"]
                }
                for message in messages
            ]
        }

        # Create JSON response for download
        response = make_response(json.dumps(conversation_json, indent=2))
        response.headers['Content-Disposition'] = f'attachment; filename=conversation_{conversation_id}.json'
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        return "Conversation not found", 404

@main.route('/conversation/<conversation_id>/export/html', methods=['POST'])
def export_conversation_html(conversation_id):
    conn = get_db_connection()
    conversation = conn.execute("SELECT * FROM Conversations WHERE conversation_id = ?", (conversation_id,)).fetchone()
    messages = conn.execute("SELECT * FROM Messages WHERE conversation_id = ?", (conversation_id,)).fetchall()
    conn.close()

    conversation_data = json.loads(conversation['conversation_data'])
    title = conversation_data.get("title", "No Title")
    create_time = conversation_data.get("create_time", "N/A")
    update_time = conversation_data.get("update_time", "N/A")

    rendered_html = render_template(
        'export_template.html',
        title=title,
        create_time=create_time,
        update_time=update_time,
        messages=messages
    )
    response = make_response(rendered_html)
    response.headers['Content-Disposition'] = f'attachment; filename=conversation_{conversation_id}.html'
    response.headers['Content-Type'] = 'text/html'
    return response

@main.route('/message/<message_id>')
def message_detail(message_id):
    with closing(get_db_connection()) as conn:
        message = conn.execute(
            "SELECT * FROM Messages WHERE message_id = ?", (message_id,)
        ).fetchone()

        if not message:
            return "Message not found.", 404

        # Fetch feedback and model comparisons for the message
        feedback = conn.execute("SELECT * FROM Feedback WHERE message_id = ?", (message_id,)).fetchall()
        model_comparisons = conn.execute("SELECT * FROM ModelComparisons WHERE message_id = ?", (message_id,)).fetchall()

    # Prepare data for the template
    message_data = {
        "message_id": message["message_id"],
        "author_role": message.get("author_role", "unknown"),
        "content": message["content"],
        "timestamp": format_timestamp(message["timestamp"]),
        "conversation_id": message["conversation_id"]
    }

    return render_template(
        'message_detail.html',
        message=message_data,
        feedback=feedback,
        model_comparisons=model_comparisons
    )

@main.route('/search', methods=['GET'])
def search():
    """
    Enhanced search endpoint to include results from Conversations and Messages tables.
    """
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    context_range = 2  # Number of messages for context

    with closing(get_db_connection()) as conn:
        # Search in the Conversations table
        conversation_query = """
            SELECT conversation_id, conversation_data
            FROM Conversations
            WHERE conversation_data LIKE ?
        """
        conversation_matches = conn.execute(conversation_query, (f'%{query}%',)).fetchall()

        # Search in the Messages table
        message_query = """
            SELECT message_id, conversation_id, content, timestamp
            FROM Messages
            WHERE content LIKE ?
        """
        message_matches = conn.execute(message_query, (f'%{query}%',)).fetchall()

        results = []

        # Process Conversation matches
        for match in conversation_matches:
            conversation_id = match['conversation_id']
            conversation_data = json.loads(match['conversation_data'])
            results.append({
                "type": "conversation",
                "conversation_id": conversation_id,
                "title": conversation_data.get("title", "No Title"),
                "content_snippet": query,
                "timestamp": format_timestamp(conversation_data.get("create_time")),
            })

        # Process Message matches with context
        for match in message_matches:
            conversation_id = match['conversation_id']
            message_id = match['message_id']

            # Fetch context messages
            context_query = """
                SELECT * FROM Messages
                WHERE conversation_id = ?
                AND create_time BETWEEN ? AND ?
            """
            context_messages = conn.execute(context_query, (
                conversation_id,
                int(message_id) - context_range,
                int(message_id) + context_range
            )).fetchall()

            results.append({
                "type": "message",
                "match": {
                    "message_id": message_id,
                    "conversation_id": conversation_id,
                    "content": match['content'],
                    "timestamp": format_timestamp(match['timestamp']),
                    "author_role": match['author_role']
                },
                "context": [
                    {
                        "message_id": msg['message_id'],
                        "content": msg['content'],
                        "timestamp": format_timestamp(msg['timestamp']),
                        "author_role": msg['author_role']
                    } for msg in context_messages
                ]
            })

        return jsonify(results)

@main.route('/recent_searches')
def recent_searches():
    """
    Retrieves and displays recent search queries.

    Fetches recent search queries from the search history JSON file using `get_recent_searches`.
    Renders the 'recent_searches.html' template with the recent searches data.
    """
    recent_searches_data = get_recent_searches()
    return render_template('recent_searches.html', recent_searches=recent_searches_data)
