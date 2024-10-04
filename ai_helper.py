import os
import openai
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_task_breakdown(task_title):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that breaks down tasks into 3-8 manageable steps."},
                {"role": "user", "content": f"Please break down the following task into 3-8 steps: {task_title}"}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Error generating task breakdown: {str(e)}")
