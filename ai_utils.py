import os
import requests
from dotenv import load_dotenv

load_dotenv()

def generate_task_breakdown(task_title):
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables")

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    prompt = f"Break down the following task into 3-8 clear, actionable steps: {task_title}"

    data = {
        'model': 'gpt-4-1106-preview',
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant that breaks down tasks into manageable steps.'},
            {'role': 'user', 'content': prompt}
        ],
        'max_tokens': 150
    }

    try:
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        response.raise_for_status()
        breakdown = response.json()['choices'][0]['message']['content'].strip()
        return breakdown
    except requests.RequestException as e:
        raise Exception(f"Error calling OpenAI API: {str(e)}")
