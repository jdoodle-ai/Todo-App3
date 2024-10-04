import os
import requests
from flask import current_app

def generate_task_breakdown(task_title):
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4-0125-preview",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that breaks down tasks into steps."},
            {"role": "user", "content": f"Break down the following task into 3-8 manageable steps: {task_title}"}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error calling OpenAI API: {str(e)}")
        raise
