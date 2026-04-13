from dotenv import load_dotenv #load_dotenv: loads values store in .env
import os

load_dotenv()  # Reads the .env file in the project directory and loads its variables into the system environment

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # in string format 
# os.getenv() only reads environment variables that already exist in the system environment.

# from config import OPENAI_API_KEY