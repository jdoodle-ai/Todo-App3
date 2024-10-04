import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def generate_task_breakdown(task_title, task_description):
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that breaks down tasks into smaller, manageable chunks."},
            {"role": "user", "content": f"Please break down the following task into 3-8 manageable steps: Title: {task_title}, Description: {task_description}"}
        ],
        "max_tokens": 150
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    breakdown = response.json()["choices"][0]["message"]["content"]
    return breakdown
