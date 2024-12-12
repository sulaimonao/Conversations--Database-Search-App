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
    log_entry = {
        "query": query,
        "start_date": start_date,
        "end_date": end_date,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    log_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'search_history.json')
    
    try:
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        if os.path.exists(log_file_path):
            with open(log_file_path, 'r+') as file:
                data = json.load(file) if file.read() else []
                data.append(log_entry)
                file.seek(0)
                json.dump(data, file, indent=4)
        else:
            with open(log_file_path, 'w') as file:
                json.dump([log_entry], file, indent=4)
    except Exception as e:
        print(f"Error writing to search history file: {e}")

def get_recent_searches(limit=5):
    log_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'search_history.json')
    try:
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r') as file:
                data = json.load(file)
                return data[-limit:]
    except Exception as e:
        print(f"Error reading search history file: {e}")
    return []
