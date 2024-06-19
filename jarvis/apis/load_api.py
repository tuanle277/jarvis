import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API keys from environment variables
api_key_1 = os.getenv('API_KEY_1')
api_key_2 = os.getenv('API_KEY_2')

if not api_key_1 or not api_key_2:
    raise ValueError("One or more API keys are missing. Please set the API_KEY_1 and API_KEY_2 environment variables.")
