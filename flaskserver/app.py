from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from flask import render_template

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
            action TEXT
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


@app.route('/admin')
def admin_page():
    return render_template('admin.html')

# Route to get logs and request count for a specific student
@app.route('/api/logs/<student_name>', methods=['GET'])
def get_logs_by_student(student_name):
    conn = sqlite3.connect('activity_logs.db')
    cursor = conn.cursor()

    # Get the logs for the student
    cursor.execute('SELECT * FROM logs WHERE student_name = ?', (student_name,))
    logs = cursor.fetchall()

    # Get the count of requests for the student
    cursor.execute('SELECT COUNT(*) FROM logs WHERE student_name = ?', (student_name,))
    request_count = cursor.fetchone()[0]
    
    conn.close()

    # Format the logs for display
    log_list = []
    for log in logs:
        log_list.append({
            'student_name': log[1],
            'timestamp': log[2],
            'url': log[3],
            'action': log[4]
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

    conn = sqlite3.connect('activity_logs.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (student_name, timestamp, url, action)
        VALUES (?, ?, ?, ?)
    ''', (student_name, data['timestamp'], data['url'], action))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})




@app.route('/view_logs')
def view_logs():
    conn = sqlite3.connect('activity_logs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT student_name, timestamp, url, action FROM logs')
    logs = cursor.fetchall()
    conn.close()

    log_list = []
    for log in logs:
        log_list.append({
            'student_name': log[0],
            'timestamp': log[1],
            'url': log[2],
            'action': log[3]
        })

    return jsonify(log_list)


if __name__ == '__main__':
    init_db()  
    app.run(host='0.0.0.0', port=5000, debug=True)
