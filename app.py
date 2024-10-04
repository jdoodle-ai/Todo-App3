from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import openai
from config import Config

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object(Config)

# Initialize the database
db = SQLAlchemy(app)

# Configure OpenAI
openai.api_key = app.config['OPENAI_API_KEY']

# Create a Task model with description field
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, default="")

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

def get_task_breakdown(task_title):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0314",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that breaks down tasks into 3-8 manageable steps."},
                {"role": "user", "content": f"Break down this task into steps: {task_title}"}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        app.logger.error(f"OpenAI API error: {str(e)}")
        return None

@app.route('/breakdown_task/<int:task_id>', methods=['POST'])
def breakdown_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    breakdown = get_task_breakdown(task.title)
    if not breakdown:
        return jsonify({"error": "Failed to generate breakdown"}), 500
    
    task.description = breakdown
    db.session.commit()
    return jsonify({"success": True, "breakdown": breakdown})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
