# Conversations Database Viewer

This project provides a comprehensive interface for managing and analyzing conversation data stored in a SQLite database. The application is built with Flask and supports various utilities such as viewing, linking, and searching through conversation records.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Setup Instructions](#setup-instructions)
3. [Usage](#usage)
   - [Running the Application](#running-the-application)
   - [Navigating the Interface](#navigating-the-interface)
4. [Scripts Overview](#scripts-overview)
   - [run.py](#runpy)
   - [app/](#app)
   - [debug_scripts/](#debug_scripts)
5. [Key Features](#key-features)
6. [Data Schema](#data-schema)
7. [Requirements](#requirements)
8. [Troubleshooting](#troubleshooting)

---

## Project Structure

The project is organized into the following main folders and files:

```plaintext
├── app/
│   ├── __init__.py               # Flask initialization
│   ├── app.py                    # Main app setup and blueprint registration
│   ├── db.py                     # Database connection utility
│   ├── parsers.py                # Parsing JSON data for conversation details
│   ├── routes.py                 # Route definitions for web interface
│   ├── utils.py                  # Utility functions (e.g., timestamp formatting)
│   ├── helpers.py                # Helper functions to fetch additional data
├── debug_scripts/
│   ├── find.py                   # Script to search for specific IDs in database tables
│   ├── link_orphan_db.py         # Script to link orphaned messages to conversations
│   ├── timestamp_fix.py          # Script to fix missing timestamps in conversation records
├── static/
│   └── style.css                 # CSS for styling the web interface
├── templates/                    # HTML templates for the app views
│   ├── index.html
│   ├── base.html
│   ├── review_orphaned_messages.html
│   ├── export_template.html
│   ├── message_detail.html
│   ├── conversation.html
├── data/
│   └── search_history.json       # JSON file to log search history
├── database.db # SQLite database file
├── requirements.txt              # Python dependencies
└── run.py                        # Script to run the Flask application
```

## Setup Instructions

1. **Clone the Repository**  
   Clone this repository to your local machine:
   ```bash
   git clone https://github.com/sulaimonao/Conversations--Database-Search-App.git
   ```

2. **Install Dependencies**  
   Install the required Python packages by running:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**  
   Ensure that the `database.db` file is present in the project root. This SQLite database stores the conversation records.

## Usage

### Running the Application

Start the Flask server with:

```bash
python run.py
```

The application will start in development mode and be accessible at `http://127.0.0.1:5000`.

### Navigating the Interface

- **Home (`/`)**: Displays a list of conversations with options to filter by date and search by keywords.
- **View Conversation**: Click on "View Conversation" in the table to see detailed messages and metadata for each conversation.
- **Review Orphaned Messages (`/review_orphaned_messages`)**: A page to review messages that lack a conversation ID and attempt to link them to appropriate conversations.

## Scripts Overview

### `run.py`

The main entry point to run the Flask application. This script imports the `app` instance from `app/app.py` and lists all registered endpoints.

### `app/`

Contains the core application files:

- **`app.py`**: Initializes the Flask app and registers the main blueprint for routing.
- **`db.py`**: Provides a utility function, `get_db_connection()`, to connect to the SQLite database.
- **`parsers.py`**: Defines the `parse_conversation_data()` function to extract message details and metadata from JSON data stored in the database.
- **`routes.py`**: Contains route handlers for the web interface, including:
  - `index()` for displaying the main list of conversations.
  - `review_orphaned_messages()` for displaying orphaned messages and linking them to conversations.
  - Routes to view, export, and interact with individual conversation data.
- **`utils.py`**: Contains helper functions like `format_timestamp()` to convert timestamps and `log_search()` to log search history in JSON.
- **`helpers.py`**: Fetches associated feedback and model comparison data for messages in conversations.

### `debug_scripts/`

Utility scripts for database maintenance and debugging:

- **`find.py`**: Searches for a specific ID across all database tables.
- **`link_orphan_db.py`**: Links orphaned messages without a conversation ID to potential matching conversations based on timestamps or content similarity.
- **`timestamp_fix.py`**: Updates `timestamp` fields in the `Conversations` table using `create_time` from JSON data where `timestamp` is missing.

## Key Features

1. **Conversation Search and Filter**: Search conversations by keywords and filter by date.
2. **View Detailed Conversation Data**: Inspect conversation messages, metadata, and additional insights.
3. **Orphaned Message Linking**: Identifies and links orphaned messages to relevant conversations.
4. **Export Conversations**: Conversations can be exported as JSON or HTML files.
5. **Search History Logging**: Logs search history to a JSON file for easy reference.

## Data Schema

The SQLite database, `database.db`, includes the following key tables:

- **`Conversations`**: Stores conversation records with fields like `conversation_id`, `user_id`, `conversation_data`, and `timestamp`.
- **`Messages`**: Stores messages linked to conversations with details such as `message_id`, `content`, `author_role`, and `timestamp`.
- **`Feedback`**: Holds user feedback data related to specific messages.
- **`ModelComparisons`**: Contains information comparing model responses for different messages.
- **`SharedConversations`**: Tracks shared versions of conversations.

## Requirements

- Python 3.x
- Flask==2.2.5
- pandas==1.5.3 (for data handling in debug scripts)

All dependencies are listed in `requirements.txt`.

## Troubleshooting

1. **Database Connection Issues**: If the app cannot connect to the database, ensure `database.db` is present in the project root.
2. **Timestamp Errors**: Use `debug_scripts/timestamp_fix.py` to update missing timestamps in the `Conversations` table.
3. **Orphaned Messages**: Run `debug_scripts/link_orphan_db.py` to link messages without conversation IDs to potential conversations.
