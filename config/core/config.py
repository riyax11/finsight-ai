import os
from dotenv import load_dotenv

load_dotenv()

# --- 1. Define Paths Robustly ---
CURRENT_FILE_PATH = os.path.abspath(__file__)
CORE_DIR = os.path.dirname(CURRENT_FILE_PATH)
PROMPTS_DIR = os.path.join(CORE_DIR, 'prompts')



def load_prompt_file(filename):
    file_path = os.path.join(PROMPTS_DIR, filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"CRITICAL ERROR: Could not find {filename} at {file_path}")
        return f"SYSTEM ERROR: Missing file: {filename}"


# --- 2. Config Class ---
class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    PROMPT_SQL_SCHEMA = load_prompt_file('schema_context.txt')
    PROMPT_SUMMARY_TEMPLATE = load_prompt_file('summary_context.txt')