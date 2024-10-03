import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_task_breakdown(task_title):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides concise task breakdowns."},
                {"role": "user", "content": f"Please provide a 2-3 sentence breakdown of the following task: {task_title}"}
            ],
            max_tokens=100
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error in OpenAI API call: {str(e)}")
        raise Exception("Failed to generate task breakdown. Please try again later.")
