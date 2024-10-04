import os
import requests
from dotenv import load_dotenv
from time import time

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
API_ENDPOINT = 'https://api.openai.com/v1/chat/completions'
MODEL = 'gpt-4'

# Simple in-memory rate limiting
LAST_REQUEST_TIME = 0
MIN_REQUEST_INTERVAL = 1  # 1 second between requests

def generate_subtasks(task_description):
    global LAST_REQUEST_TIME

    # Rate limiting
    current_time = time()
    if current_time - LAST_REQUEST_TIME < MIN_REQUEST_INTERVAL:
        raise Exception('Rate limit exceeded. Please try again in a moment.')

    LAST_REQUEST_TIME = current_time

    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }

    data = {
        'model': MODEL,
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant that breaks down tasks into subtasks.'},
            {'role': 'user', 'content': f'Break down this task into 3-8 manageable steps: {task_description}'}
        ],
        'max_tokens': 150
    }

    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        subtasks = result['choices'][0]['message']['content']
        return subtasks
    except requests.exceptions.RequestException as e:
        raise Exception(f'Error calling OpenAI API: {str(e)}')
    except (KeyError, IndexError) as e:
        raise Exception(f'Error processing OpenAI response: {str(e)}')
