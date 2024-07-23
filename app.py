from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import random
import string

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts_calls.db'
db = SQLAlchemy(app)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(120))
    phone_numbers = db.Column(db.Text)
    emails = db.Column(db.Text)

class CallLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    number = db.Column(db.String(50))
    call_type = db.Column(db.String(50))
    duration = db.Column(db.Integer)
    timestamp = db.Column(db.String(50))
    unique_id = db.Column(db.String(8), unique=True)

def generate_unique_id():
    return ''.join(random.choices(string.digits, k=8))

@app.route('/api/save_data', methods=['POST'])
def save_data():
    data = request.get_json()
    contacts = data['contacts']
    call_logs = data['callLogs']

    for contact in contacts:
        new_contact = Contact(
            display_name=contact['displayName'],
            phone_numbers=','.join(contact['phones']) if contact['phones'] else '',
            emails=','.join(contact['emails']) if contact['emails'] else ''
        )
        db.session.add(new_contact)

    for log in call_logs:
        new_log = CallLog(
            name=log['name'],
            number=log['number'],
            call_type=log['callType'],
            duration=log['duration'],
            timestamp=datetime.fromtimestamp(log['timestamp'] / 1000).isoformat() if log['timestamp'] else None,
            unique_id=generate_unique_id()
        )
        db.session.add(new_log)

    db.session.commit()
    return jsonify({'message': 'Data saved successfully'}), 200

@app.route('/call_logs', methods=['GET'])
def call_logs():
    logs = CallLog.query.all()
    return render_template('call_logs.html', call_logs=logs)

@app.route('/delete_call_log/<int:id>', methods=['POST'])
def delete_call_log(id):
    log = CallLog.query.get_or_404(id)
    db.session.delete(log)
    db.session.commit()
    return jsonify({'message': 'Call log deleted successfully'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
