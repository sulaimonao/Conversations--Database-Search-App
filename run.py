# run.py
from app.app import app  # This imports the Flask app instance with all routes registered

print("Registered Endpoints:")
for rule in app.url_map.iter_rules():
    print(f"Endpoint: {rule.endpoint}, URL: {rule}")

if __name__ == '__main__':
    app.run(debug=True)
