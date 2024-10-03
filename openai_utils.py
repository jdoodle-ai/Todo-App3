import openai
import os

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_task_description(task_title):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides concise task breakdowns."},
                {"role": "user", "content": f"Please provide a 2-3 sentence breakdown of the task: {task_title}"}
            ],
            max_tokens=100
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error generating task description: {str(e)}")
        raise
