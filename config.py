import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

def configure_gemini():
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    return genai.GenerativeModel('gemini-2.0-flash',
        generation_config={
            'temperature': 0.1,
            'candidate_count': 1,
            'max_output_tokens': 512,
            'stream': True
        }
    )