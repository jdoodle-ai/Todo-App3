from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import openai
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Set up OpenAI API key
openai.api_key = 'your-api-key-here'  # Replace with your actual API key

# Set up caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Set up rate limiting
limiter = Limiter(app, key_func=get_remote_address)

# Create a Task model with description field
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, default="")  # New field to store markdown text

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

@cache.memoize(timeout=3600)  # Cache for 1 hour
def get_ai_description(task_title):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates task breakdowns."},
                {"role": "user", "content": f"Generate a 2-3 sentence breakdown for the task: {task_title}"}
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return str(e)

@app.route('/generate_description/<int:task_id>', methods=['POST'])
@limiter.limit("5 per minute")
def generate_description(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    try:
        description = get_ai_description(task.title)
        task.description = description
        db.session.commit()
        return jsonify({'description': description})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
