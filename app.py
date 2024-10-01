from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import requests

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
    description = db.Column(db.Text, default="")  # New field to store markdown text
    subtasks = db.Column(db.Text, default="")  # New field to store subtasks


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
def generate_subtasks(task_id):
    task = Task.query.get(task_id)
    if task:
        api_key = os.getenv('OPENAI_API_KEY')
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'gpt-4o',
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an AI assistant that helps users divide their tasks into subtasks using OpenAI API. Only return a maximum of 6 subtasks and nothing else. Use the ChatCompletion endpoint.'
                },
                {
                    'role': 'user',
                    'content': task.description
                }
            ]
        }
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        if response.status_code == 200:
            subtasks = response.json().get('choices')[0].get('message').get('content').strip().split('\n')
            task.subtasks = '\n'.join(subtasks)
            db.session.commit()
    return redirect(url_for('index'))





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
