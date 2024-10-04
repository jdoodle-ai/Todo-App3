import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_subtasks(task_title):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that breaks down tasks into subtasks."},
                {"role": "user", "content": f"Break down the following task into 3-8 subtasks: {task_title}"}
            ],
            max_tokens=150
        )
        subtasks = response.choices[0].message['content'].strip().split('\n')
        return [subtask.strip('- ') for subtask in subtasks if subtask.strip()]
    except Exception as e:
        raise Exception(f"Error generating subtasks: {str(e)}")
