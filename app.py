from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import openai
from functools import wraps
import time
import os

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Configure OpenAI API
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Create a Task model with description field
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, default="")

# Rate limiting decorator
def rate_limit(limit=5, per=60):
    def decorator(f):
        last_reset = time.time()
        calls = 0
        @wraps(f)
        def wrapped(*args, **kwargs):
            nonlocal last_reset, calls
            now = time.time()
            if now - last_reset > per:
                calls = 0
                last_reset = now
            if calls >= limit:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            calls += 1
            return f(*args, **kwargs)
        return wrapped
    return decorator

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

@app.route('/generate_breakdown/<int:task_id>', methods=['POST'])
@rate_limit(limit=5, per=60)
def generate_breakdown(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides brief task breakdowns."},
                {"role": "user", "content": f"Provide a 2-3 sentence breakdown of steps to complete the following task: {task.title}"}
            ]
        )
        breakdown = response.choices[0].message['content'].strip()
        
        task.description = breakdown
        db.session.commit()
        
        return jsonify({'description': breakdown})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
