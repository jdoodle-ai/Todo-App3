import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_task_breakdown(task_title):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides concise task breakdowns."},
                {"role": "user", "content": f"Provide a 2-3 sentence breakdown of steps required to complete this task: {task_title}"}
            ],
            max_tokens=150
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error in generating task breakdown: {str(e)}")
        raise