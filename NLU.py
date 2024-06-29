'''
Testing purpose only
'''

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import spacy
import json
import os
import platform

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

class TextPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

    def preprocess(self, text):
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word.lower() not in self.stop_words]
        tokens = [self.lemmatizer.lemmatize(word) for word in tokens]
        return tokens

class IntentRecognizer:
    def __init__(self):
        self.model = make_pipeline(TfidfVectorizer(), MultinomialNB())

    def train(self, X, y):
        self.model.fit(X, y)

    def predict(self, text):
        return self.model.predict([text])[0]

class EntityRecognizer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def recognize(self, text):
        doc = self.nlp(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities

class CommandExecutor:
    def __init__(self, json_path):
        with open(json_path, 'r') as f:
            self.intent_commands = json.load(f)
    
    def execute_command(self, intent, entities=None):
        system = platform.system().lower()
        if intent in self.intent_commands:
            command = self.intent_commands[intent].get(f'{system}_command')
            if command:
                os.system(command)
            else:
                print(f"No command found for {intent} on {system}")
        else:
            print(f"Unknown intent: {intent}")

class NLU:
    def __init__(self, json_path):
        self.preprocessor = TextPreprocessor()
        self.intent_recognizer = IntentRecognizer()
        self.entity_recognizer = EntityRecognizer()
        self.command_executor = CommandExecutor(json_path)
    
    def train_intent_recognizer(self, X_train, y_train):
        self.intent_recognizer.train(X_train, y_train)
    
    def process(self, text):
        tokens = self.preprocessor.preprocess(text)
        intent = self.intent_recognizer.predict(" ".join(tokens))
        entities = self.entity_recognizer.recognize(text)
        self.command_executor.execute_command(intent, entities)

# Example training data
X_train = [
    "What is the weather like in New York tomorrow?",
    "Set an alarm for 7 AM.",
    "Play some music.",
    "What time is it?",
    "Tell me a joke.",
    "Open Notepad",
    "Open Calculator",
    "Shutdown the computer",
    "Restart the computer"
]
y_train = [
    "GetWeather",
    "SetAlarm",
    "PlayMusic",
    "GetTime",
    "TellJoke",
    "OpenNotepad",
    "OpenCalculator",
    "Shutdown",
    "Restart"
]

if __name__ == "__main__":
    nlu = NLU('intent_commands.json')
    nlu.train_intent_recognizer(X_train, y_train)

    # Example usage
    text = "What time is it?"
    nlu.process(text)
    
    text = "Play some music."
    nlu.process(text)
    
    text = "Cal"
    nlu.process(text)
    
    # text = "Shutdown the computer"
    # nlu.process(text)
