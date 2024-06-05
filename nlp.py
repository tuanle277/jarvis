# nlp.py

# OpenAI
import openai

openai.api_key = 'YOUR_OPENAI_API_KEY'

def get_response(prompt):
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

if __name__ == "__main__":
    prompt = "What is the weather like today?"
    response = get_response(prompt)
    print(response)

# Gemini API

# To install the Python SDK, use this CLI command:
# pip install google-cloud-aiplatform

import vertexai
from vertexai.generative_models import GenerativeModel, Image, Part

class GeminiAI:
    def __init__(self, project_id: str, region: str) -> None:
        vertexai.init(project=project_id, location=region)
        self.model = GenerativeModel('gemini-1.5-flash')

    def text_from_prompt(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    def text_from_image(self, path: str, prompt: str) -> str:
        image = Image.load_from_file(path)
        response = self.model.generate_content([prompt, image])
        return response.text

    def text_from_chat(self, chat: str) -> str:
        chat_session = self.model.start_chat()
        response = chat_session.send_message(chat)
        return response.text

    def text_from_video(self, path: str, prompt: str) -> str:
        video_file = Part.from_uri(path, mime_type="video/mp4")
        contents = [video_file, prompt]
        response = self.model.generate_content(contents)
        return response.text