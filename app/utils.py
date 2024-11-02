# app/utils.py

import json
from datetime import datetime
import os

def format_timestamp(unix_timestamp):
    """
    Formats a Unix timestamp into a human-readable date and time string.

    Args:
        unix_timestamp: The Unix timestamp to format (can be str, int, or float).
    """
    try:
        return datetime.fromtimestamp(float(unix_timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return "N/A"

def log_search(query, start_date, end_date):
    """Log each search query to a JSON file with timestamp."""
    log_entry = {
        "query": query,
        "start_date": start_date,
        "end_date": end_date,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    log_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'search_history.json')
    
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    # Append the new log entry to the JSON file
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r+') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []
            data.append(log_entry)
            file.seek(0)
            json.dump(data, file, indent=4)
    else:
        with open(log_file_path, 'w') as file:
            json.dump([log_entry], file, indent=4)

def get_recent_searches(limit=5):
    """Retrieve the most recent search queries from the search history JSON."""
    log_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'search_history.json')
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as file:
            try:
                data = json.load(file)
                return data[-limit:]  # Return the last `limit` entries
            except json.JSONDecodeError:
                return []
    return []
    

def get_recent_searches(limit=5):
    """
    Retrieve the most recent search queries from the search history JSON file.

    Args:
        limit: The maximum number of recent searches to retrieve (default is 5).

    Returns:
        A list of dictionaries, where each dictionary represents a search query 
        with 'query', 'start_date', 'end_date', and 'timestamp' keys. 
        Returns an empty list if the log file does not exist or is empty.
    """
    log_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'search_history.json')
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as file:
            try:
                data = json.load(file)
                return data[-limit:]  # Return the last `limit` entries
            except json.JSONDecodeError:
                return []
    return []
