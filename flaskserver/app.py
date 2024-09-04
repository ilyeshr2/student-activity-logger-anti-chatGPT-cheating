from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# Initialize the database
def init_db():
    conn = sqlite3.connect('activity_logs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            url TEXT NOT NULL,
            action TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Route to log activity
@app.route('/api/log', methods=['POST'])
def log_activity():
    data = request.json
    print(f"Received data: {data}")  # Debugging statement
    if not data or 'timestamp' not in data or 'url' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400
     
    action = data.get('action', 'Unknown Action')  # Default value if 'action' is missing
    
    conn = sqlite3.connect('activity_logs.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (timestamp, url, action)
        VALUES (?, ?, ?)
    ''', (data['timestamp'], data['url'], action))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})


# Route to view logs
@app.route('/view_logs')
def view_logs():
    conn = sqlite3.connect('activity_logs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM logs')
    logs = cursor.fetchall()
    conn.close()
    return jsonify(logs)

if __name__ == '__main__':
    init_db()  
    app.run(host='0.0.0.0', port=5000, debug=True)
