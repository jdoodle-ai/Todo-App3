import requests
import os

def get_task_breakdown(task_title, task_description):
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a task breakdown assistant. Given a task title and description, break it down into 3-8 manageable steps."},
            {"role": "user", "content": f"Task: {task_title}\nDescription: {task_description}\nPlease break this task down into 3-8 manageable steps."}
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    response.raise_for_status()

    breakdown = response.json()['choices'][0]['message']['content'].strip()
    return breakdown
