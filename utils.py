import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_task_breakdown(task_title):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that breaks down tasks into manageable steps."},
                {"role": "user", "content": f"Break down the following task into 3-8 steps: {task_title}"}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None
