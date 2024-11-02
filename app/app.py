# app/app.py
from flask import Flask
import os
from app.routes import main  # absolute Import
from .db import get_db_connection
from .utils import format_timestamp
from flask import request

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'),
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')
)

# Register the Blueprint
app.register_blueprint(main)

@app.context_processor
def inject_search_params():
    query = request.args.get('query', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    return {'query': query, 'start_date': start_date, 'end_date': end_date}
