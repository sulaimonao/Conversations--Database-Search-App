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
│   ├── add_timestamp.py          # Migrates and updates 'timestamp' fields in Conversations table
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
├── GPT_conversations_database.db # SQLite database file 
├── requirements.txt              # Python dependencies
└── run.py                        # Script to run the Flask application
```

---

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
   Ensure that the `GPT_conversations_database.db` file is present in the project root. This SQLite database stores the conversation records.

   - If you encounter issues with missing or outdated columns, run the `debug_scripts/add_timestamp.py` script to migrate and update the `timestamp` column.

---

## Usage

### Running the Application

Start the Flask server with:

```bash
python run.py
```

The application will start in development mode and be accessible at `http://127.0.0.1:5000`.

### Navigating the Interface

- **Home (`/`)**: Displays a list of conversations with options to filter by date and search by keywords.
- **View Conversation**: Click on a conversation to view detailed messages and metadata.
- **Review Orphaned Messages (`/review_orphaned_messages`)**: A page to review and link messages lacking a conversation ID.

---

## Scripts Overview

### `run.py`

The main entry point to run the Flask application. This script imports the `app` instance and lists all registered endpoints.

### `app/`

Contains the core application files, including:

- **`parsers.py`**: Defines `parse_conversation_data()` to process conversation and message metadata.
- **`routes.py`**: Provides endpoints for viewing, searching, and exporting conversation data.
- **`db.py`**: Supplies a reusable database connection via `get_db_connection()`.

### `debug_scripts/`

Scripts to assist with database maintenance:

- **`add_timestamp.py`**: Adds and populates the `timestamp` column in the `Conversations` table.
- **`link_orphan_db.py`**: Links orphaned messages to appropriate conversations based on timestamps.
- **`timestamp_fix.py`**: Fixes `timestamp` data in cases where it is null.

---

## Key Features

1. **Conversation Search and Filter**: Search conversations by keywords and filter by date.
2. **Detailed View**: Inspect conversation messages, metadata, and additional insights.
3. **Orphaned Message Linking**: Automatically link orphaned messages to potential conversations.
4. **Export Options**: Export conversations as JSON or HTML files.
5. **Database Maintenance Tools**: Scripts for troubleshooting and updating the database.

---

## Data Schema

### Key Tables:

1. **`Conversations`**
   - **Columns**: `conversation_id`, `title`, `create_time`, `update_time`, `timestamp`

2. **`Messages`**
   - **Columns**: `message_id`, `conversation_id`, `content`, `author_role`, `create_time`

3. **`Feedback`**
   - Stores user feedback linked to specific messages.

4. **`ModelComparisons`**
   - Logs model-generated comparison data.

---

## Requirements

- Python 3.10+
- Flask==2.2.5
- pandas==1.5.3

---

## Troubleshooting

1. **Database Issues**
   - Run `debug_scripts/add_timestamp.py` if the `timestamp` column is missing or outdated.
   - Ensure `GPT_conversations_database.db` is in the root directory.

2. **Parsing Errors**
   - Confirm all conversation data adheres to the expected schema with valid `conversation_data`.

3. **Search Issues**
   - Validate the `search_history.json` file format and its path in the `data/` directory.