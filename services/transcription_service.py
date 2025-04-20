import time
import requests


class TranscriptionService:
    """Handles audio transcription using Deepgram API"""

    def __init__(self, api_key=None):
        self.api_key = api_key

    def set_api_key(self, api_key):
        """Update the API key"""
        self.api_key = api_key

    def transcribe(self, audio_file, model="nova-3"):
        """Transcribe audio file using Deepgram API"""
        if not self.api_key:
            raise ValueError("API key is not set")

        # Define the URL for the Deepgram API endpoint
        query_params = {
            "model": model,
            "smart_format": 'true',
            "punctuate": 'true',
            "detect_language": 'true'
        }
        url = "https://api.deepgram.com/v1/listen"
        url += "?" + "&".join(f"{key}={value}" for key,
                              value in query_params.items())

        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "audio/*"
        }

        start_time = time.time()

        with open(audio_file, 'rb') as file:
            response = requests.post(url, headers=headers, data=file)

        # Process the response
        response_json = response.json()
        transcript = response_json['results']['channels'][0]['alternatives'][0]['transcript']

        print(
            f"Transcription completed in {time.time() - start_time:.2f} seconds")
        return transcript
