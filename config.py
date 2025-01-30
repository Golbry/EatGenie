import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
    OLLAMA_URL = os.environ.get('OLLAMA_URL') or 'http://localhost:11434' 