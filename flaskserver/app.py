from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import requests

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('activity_logs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            url TEXT NOT NULL,
            action TEXT,
            message TEXT  
        )
    ''')
    conn.commit()
    conn.close()

def get_action_from_url(url):
    if 'backend-api' in url:
        return 'Backend API Call'
    elif 'public-api' in url:
        return 'Public API Call'
    elif 'ces/v1' in url:
        return 'CES API Call'
    elif url.endswith('.js'):
        return 'JavaScript File Request'
    elif url.endswith('favicon.ico'):
        return 'Favicon Request'
    elif url == 'https://chatgpt.com/':
        return 'Page Visit'
    return 'Unknown Action'

def fetch_message_from_url(url):
    if 'conversation' not in url:
        return None

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "messages" in data:
            messages = data["messages"]
            for message in messages:
                if message["author"]["role"] == "user":
                    return message["content"]["parts"][0]  # Return the user message
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    return None


@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/api/logs/<student_name>', methods=['GET'])
def get_logs_by_student(student_name):
    conn = sqlite3.connect('activity_logs.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM logs WHERE student_name = ?', (student_name,))
    logs = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) FROM logs WHERE student_name = ?', (student_name,))
    request_count = cursor.fetchone()[0]
    
    conn.close()

    log_list = []
    for log in logs:
        log_list.append({
            'student_name': log[1],
            'timestamp': log[2],
            'url': log[3],
            'action': log[4],
            'message': log[5]  # Include the message
        })

    return jsonify({
        'logs': log_list,
        'request_count': request_count
    })

@app.route('/api/log', methods=['POST'])
def log_activity():
    data = request.json
    print(f"Received data: {data}")

    if not data or 'timestamp' not in data or 'url' not in data or 'studentName' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

    action = get_action_from_url(data['url'])
    student_name = data['studentName']
    message = fetch_message_from_url(data['url'])  # Fetch message from the URL

    conn = sqlite3.connect('activity_logs.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (student_name, timestamp, url, action, message)
        VALUES (?, ?, ?, ?, ?)
    ''', (student_name, data['timestamp'], data['url'], action, message))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})

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
    app.run(debug=True)
