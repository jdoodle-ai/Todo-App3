from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from openai_utils import generate_subtasks
from datetime import datetime, timedelta

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Create a Task model with description field
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, default="")
    subtasks = db.Column(db.Text, default="")
    last_ai_request = db.Column(db.DateTime)

# Route for the homepage
@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

# Route to add a new task
@app.route('/add', methods=['POST'])
def add_task():
    task_title = request.form.get('title')
    if task_title:
        new_task = Task(title=task_title)
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/update_description/<int:task_id>', methods=['POST'])
def update_description(task_id):
    task = Task.query.get(task_id)
    if task:
        task.description = request.form.get('description')
        db.session.commit()
    return redirect(url_for('index'))

# Route to delete a task
@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>', methods=['GET'])
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.completed = not task.completed  # Toggle the completed status
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/generate_subtasks/<int:task_id>', methods=['POST'])
def generate_subtasks_route(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    # Check if the last AI request was made less than 1 minute ago
    if task.last_ai_request and datetime.utcnow() - task.last_ai_request < timedelta(minutes=1):
        return jsonify({'error': 'Please wait before making another AI request'}), 429

    try:
        subtasks = generate_subtasks(task.title)
        task.subtasks = '\n'.join(subtasks)
        task.last_ai_request = datetime.utcnow()
        db.session.commit()
        return jsonify({'subtasks': subtasks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
