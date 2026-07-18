import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")


MODEL = "llama-3.3-70b-versatile"


TEMPERATURE = 0.7


MAX_TOKENS = 1024
