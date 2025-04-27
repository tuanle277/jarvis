import openai
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import vertexai
from vertexai.generative_models import GenerativeModel, Image, Part


class ChatBotModule:
    def __init__(self, model_type: str, **kwargs):
        self.model_type = model_type.lower()
        if self.model_type == "openai":
            self.chatbot = OpenAIChat(**kwargs)
        elif self.model_type == "diablo":
            self.chatbot = DiabloChat(**kwargs)
        elif self.model_type == "gemini":
            self.chatbot = GeminiChat(**kwargs)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    def get_response(self, prompt: str):
        return self.chatbot.get_response(prompt)


class OpenAIChat:
    def __init__(self, api_key: str) -> None:
        openai.api_key = api_key

    def get_response(self, prompt: str) -> str:
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()


class DiabloChat:
    def __init__(self) -> None:
        model_name = "microsoft/DialoGPT-medium"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.conversation_history = []
        self.chatbot = pipeline('conversational', model='microsoft/DialoGPT-medium')

    def get_response(self, prompt: str) -> str:
        conversation = self.chatbot(prompt)
        self.conversation_history.append(conversation)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_length=150)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    
    def response(self, prompt):
        """Generates a response using DialoGPT for conversational responses."""
        conversation = Conversation(prompt)
        self.conversation_history.append(conversation)
        response = self.chatbot(self.conversation_history)
        return response[-1]["content"]

class GeminiChat:
    def __init__(self, project_id: str, region: str) -> None:
        vertexai.init(project=project_id, location=region)
        self.model = GenerativeModel('gemini-1.5-flash')

    def get_response(self, prompt: str) -> str:
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
