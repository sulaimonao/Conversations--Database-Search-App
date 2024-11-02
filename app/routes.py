# app/routes.py
from flask import Blueprint, render_template, request, make_response
from .db import get_db_connection
from .utils import format_timestamp, log_search, get_recent_searches
from .parsers import parse_conversation_data
from .helpers import fetch_feedback, fetch_model_comparisons
import json
from datetime import datetime
import math
import logging
from contextlib import closing

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Retrieve query parameters for search, date range, pagination, sorting
    query = request.args.get('query', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    # Database connection
    with closing(get_db_connection()) as conn:
        sql_query = "SELECT * FROM Conversations WHERE 1=1"
        params = []

        # Apply search and date filters
        if query:
            sql_query += " AND conversation_data LIKE ?"
            params.append(f'%{query}%')
        if start_date:
            sql_query += " AND datetime(timestamp, 'unixepoch') >= ?"
            params.append(start_date)
        if end_date:
            sql_query += " AND datetime(timestamp, 'unixepoch') <= ?"
            params.append(end_date)

        # Calculate total number of matching records (for total pages)
        count_query = "SELECT COUNT(*) FROM Conversations WHERE 1=1"
        count_params = params.copy()
        total_records = conn.execute(count_query, count_params).fetchone()[0]
        total_pages = math.ceil(total_records / per_page)

        # Fetch conversations without SQL sorting
        sql_query += " LIMIT ? OFFSET ?"
        params.extend([per_page, offset])
        conversations = conn.execute(sql_query, params).fetchall()

        # Process and parse JSON data for sorting in Python
        results = []
        for conversation in conversations:
            conversation_id = conversation['conversation_id']
            user_id = conversation['user_id']
            timestamp = format_timestamp(conversation['timestamp'])
            parsed_data = parse_conversation_data(conversation['conversation_data'])

            # Extract create_time and update_time from parsed_data if available
            create_time = parsed_data.get("create_time")
            update_time = parsed_data.get("update_time")

            # Extract and summarize unique roles, limit to 5 for brevity
            unique_roles = list(set(msg.get("author_role") for msg in parsed_data["messages"]))
            summarized_roles = ", ".join(unique_roles[:5]) + ("..." if len(unique_roles) > 5 else "")

            results.append({
                "conversation_id": conversation_id,
                "user_id": user_id,
                "timestamp": timestamp,
                "title": parsed_data["title"],
                "create_time": create_time,
                "update_time": update_time,
                "mapping_ids": summarized_roles  # Summarized unique roles
            })

        # Sort results in Python
        sort_by = request.args.get('sort_by', 'timestamp')
        order = request.args.get('order', 'DESC')
        reverse_order = (order == 'DESC')
        valid_sort_fields = ['timestamp', 'create_time', 'update_time']

        # Sort only if valid field
        if sort_by in valid_sort_fields:
            results.sort(key=lambda x: x.get(sort_by) or '', reverse=reverse_order)

    # Pass the sort field, order, and pagination details to the template
    return render_template(
        'index.html',
        conversations=results,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        sort_by=sort_by,
        order=order,
        query=query,
        start_date=start_date,
        end_date=end_date
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

@main.route('/conversation/<conversation_id>')
def conversation(conversation_id):
    with closing(get_db_connection()) as conn:
        # Retrieve conversation details from `Conversations` table
        conversation = conn.execute(
            "SELECT * FROM Conversations WHERE conversation_id = ?", (conversation_id,)
        ).fetchone()
        
        if not conversation:
            return "Conversation not found", 404

        # Parse the conversation_data JSON field
        parsed_data = parse_conversation_data(conversation['conversation_data'])

        # Retrieve associated messages from `Messages` table
        messages = conn.execute(
            "SELECT * FROM Messages WHERE conversation_id = ?", (conversation_id,)
        ).fetchall()

        # Retrieve feedback related to messages from `Feedback` table
        message_ids = [msg['message_id'] for msg in messages]
        feedback_data = conn.execute(
            "SELECT * FROM Feedback WHERE message_id IN ({})".format(
                ",".join("?" for _ in message_ids)), message_ids
        ).fetchall()

        # Retrieve model comparisons related to messages from `ModelComparisons` table
        model_comparisons = conn.execute(
            "SELECT * FROM ModelComparisons WHERE message_id IN ({})".format(
                ",".join("?" for _ in message_ids)), message_ids
        ).fetchall()

        # Retrieve associated shared conversations from `SharedConversations` table
        shared_conversations = conn.execute(
            "SELECT * FROM SharedConversations WHERE conversation_id = ?", (conversation_id,)
        ).fetchall()

    # Pass all retrieved data to the template
    return render_template(
        'conversation.html',
        title=parsed_data["title"],
        create_time=parsed_data["create_time"],
        update_time=parsed_data["update_time"],
        messages=parsed_data["messages"],  # Use parsed messages from `conversation_data`
        raw_messages=messages,  # Raw messages directly from the `Messages` table
        feedback=feedback_data,
        model_comparisons=model_comparisons,
        shared_conversations=shared_conversations,
        conversation_id=conversation_id
    )

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
@main.route('/search', methods=['POST'])
def search_conversations():
    """
    Handles search requests for conversations based on query parameters.

    Retrieves conversations from the database based on the provided query, start date, and end date.
    Logs the search query using the `log_search` function.
    Redirects to the main index page with the search parameters included in the URL.
    """
    query = request.form.get('query', '')
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')

    log_search(query, start_date, end_date)  # Log the search query

    return redirect(url_for('main.index', query=query, start_date=start_date, end_date=end_date))

@main.route('/recent_searches')
def recent_searches():
    """
    Retrieves and displays recent search queries.

    Fetches recent search queries from the search history JSON file using `get_recent_searches`.
    Renders the 'recent_searches.html' template with the recent searches data.
    """
    recent_searches_data = get_recent_searches()
    return render_template('recent_searches.html', recent_searches=recent_searches_data)
