import os
import openai
import requests
import json
from dotenv import load_dotenv
import pysrt

load_dotenv()

openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.Model.list()
input_file_location = "" #e.g. C:/somewhere.mp3
output_file_location = "" #e.g. C:/somewhere.srt

url = 'https://api.openai.com/v1/audio/transcriptions' #transcriptions or #translations
headers = {
    'Authorization': 'Bearer ' + openai.api_key
}
data = {
    'model': 'whisper-1',
    'response_format': 'srt',
    'prompt': 'doujinshi',
    'language': 'ja', #not for translations
}
files = {
    'file': ('audio.mp3', open(input_file_location, 'rb'))
}

response = requests.post(url, headers=headers, data=data, files=files)

with open(output_file_location, "wb") as f:
    f.write(response.content)