# app/parsers.py
import json
from .utils import format_timestamp

def parse_conversation_data(conversation_data):
    def extract_messages(mapping, messages, level=0):
        if not mapping:
            return

        message_info = mapping.get("message")
        if message_info and isinstance(message_info, dict):
            author_role = message_info.get("author", {}).get("role", "unknown")
            content_parts = message_info.get("content", {}).get("parts", [])
            
            # Ensure content_parts contains only strings before joining
            content = "\n".join(str(part) for part in content_parts if isinstance(part, str)) or "Content unavailable"
            timestamp_raw = message_info.get("create_time")
            timestamp = format_timestamp(timestamp_raw)
            
            messages.append({
                "message_id": message_info.get("id"),
                "author_role": author_role,
                "content": content,
                "timestamp": timestamp,
                "timestamp_raw": timestamp_raw,
                "level": level  # Set level for indentation
            })

        children_ids = mapping.get("children", [])
        for child_id in children_ids:
            child_mapping = mappings.get(child_id)
            if child_mapping:
                extract_messages(child_mapping, messages, level + 1)

    try:
        data = json.loads(conversation_data)
        title = data.get("title", "No Title")
        create_time = format_timestamp(data.get("create_time"))
        update_time = format_timestamp(data.get("update_time"))
        mappings = data.get("mapping", {})
        messages = []
        special_id = data.get("special_id", "N/A")  # Assume 'special_id' is the correct key

        for key, mapping in mappings.items():
            extract_messages(mapping, messages)

        messages.sort(key=lambda x: x['timestamp_raw'] or 0)
        mapping_ids_str = ", ".join(str(msg.get("author_role", "")) for msg in messages)

        return {
            "title": title,
            "create_time": create_time,
            "update_time": update_time,
            "mapping_ids": mapping_ids_str,
            "special_id": special_id, 
            "messages": messages
        }

    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error parsing conversation data: {e}")
        return {
            "title": "No Title",
            "create_time": "N/A",
            "update_time": "N/A",
            "mapping_ids": "No mappings",
            "mapping_ids": "No mappings",
            "special_id": "N/A",
            "messages": []
        }