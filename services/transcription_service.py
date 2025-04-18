import time
from openai import OpenAI

class TranscriptionService:
    """Handles audio transcription using OpenAI API"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        
    def set_api_key(self, api_key):
        """Update the API key"""
        self.api_key = api_key
        
    def transcribe(self, audio_file, model="gpt-4o-mini-transcribe"):
        """Transcribe audio file using OpenAI API"""
        if not self.api_key:
            raise ValueError("API key is not set")
            
        client = OpenAI(api_key=self.api_key)
        
        start_time = time.time()
        with open(audio_file, 'rb') as file:
            response = client.audio.transcriptions.create(
                model=model,
                file=file
            )
        
        print(f"Transcription completed in {time.time() - start_time:.2f} seconds")
        return response.text
