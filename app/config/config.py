import os
from dotenv import load_dotenv

load_dotenv()

ALPHA_API_KEY = os.getenv("ALPHA_API_KEY")
DEFAULT_SYMBOL = os.getenv("SYMBOL", "AAPL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")