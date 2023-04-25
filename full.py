from pydub import AudioSegment
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

audio_folder_path = "" #filepath to .mp3 directory aka 'C:/music/'
audio_file_name = "" #name of mp3 file without .mp3 aka for cool.mp3 just use 'cool'
audio_language = "en" #language to process file in. https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
ai_prompt = "" #additional prompt for context to Whisper. Be creative.

def get_segment_times(audio_path, segment_length):
    # Open the audio file
    audio = AudioSegment.from_mp3(audio_path)
    
    # Get the total length of the audio file in milliseconds
    audio_length = len(audio)
    
    # Calculate the number of segments needed
    num_segments = audio_length // (segment_length * 1000)
    
    # Calculate the start and end times for each segment
    segment_times = []
    for i in range(num_segments):
        start_time = i * segment_length * 1000
        end_time = (i + 1) * segment_length * 1000
        segment_times.append((start_time, end_time))
    
    # Add an extra segment for any remaining audio at the end
    if audio_length % (segment_length * 1000) != 0:
        start_time = num_segments * segment_length * 1000
        end_time = audio_length
        segment_times.append((start_time, end_time))
    
    return segment_times

def extract_segment(audio, start_time, end_time):  
    # Extract the segment
    segment = audio[start_time:end_time]
    
    # Define a temporary filename based on the start and end times
    temp_filename = f"{audio_folder_path}{start_time}_{end_time}.mp3"
    
    # Save the segment to the temporary file
    segment.export(f"{temp_filename}", format="mp3")
    
    return temp_filename

def transcribe_audio(audio_path, srt_filename):
    url = 'https://api.openai.com/v1/audio/transcriptions' #transcriptions #translations
    headers = {
        'Authorization': 'Bearer ' + openai.api_key
    }
    data = {
        'model': 'whisper-1',
        'response_format': 'srt',
        'prompt': ai_prompt,
        'language': audio_language, #not for translations
    }
    files = {
        'file': ('audio.mp3', open(audio_path, 'rb'))
    }

    response = requests.post(url, headers=headers, data=data, files=files)

    with open(srt_filename, "wb") as f:
        f.write(response.content)

def combine_srt_files(srt_files, output_path):
    # Open each SRT files and append to combined SRT
    combined_srt = pysrt.SubRipFile()
    time_skip = 0
    for srt_file in srt_files:
        #trim each srt to a strict 20 minutes
        sub = pysrt.open(srt_file, encoding='utf-8')
        try:
            sub[-1].end.minutes = 20
            sub[-1].end.seconds = 0
            sub.shift(minutes=time_skip)
            time_skip += 20
            combined_srt += sub
        except:
            pass            

    # Save the combined SRT to the output file
    combined_srt.save(output_path, encoding='utf-8')

def fix_srt_file(srt_file_path):
    # Open the input file for reading
    with open(srt_file_path, 'r', encoding='utf-8') as input_file:
        # Open the output file for writing
        with open(f"{audio_folder_path}{audio_file_name}_FINAL.srt", 'w', encoding='utf-8') as output_file:
            sub_line_num = 1
            file_line_num = 0
            last_sub_text = ""
            # Iterate over each line in the input file
            for line in input_file:
                file_line_num += 1
                # Check if the line contains a single integer
                if line.strip().isdigit():
                    # Convert the line to an integer
                    number = sub_line_num
                    # Increment
                    sub_line_num += 1
                    # Write the resulting number to the output file
                    output_file.write(str(number) + '\n')
                else:
                    # Write the original line to the output file unless its a repeat of the previous sub
                    if(file_line_num % 4 == 3):
                        if(line != last_sub_text):
                            last_sub_text = line
                            output_file.write(line)
                        else:
                            output_file.write('\n')
                    else:
                        output_file.write(line)
                                            

# Get the segment times
segment_times = get_segment_times(f"{audio_folder_path}{audio_file_name}.mp3", 1200)

# Generate SRT files and save them to a list
srt_files = []

# Open the audio file
audio = AudioSegment.from_file(f"{audio_folder_path}{audio_file_name}.mp3")

# Extract each segment and process it
for start_time, end_time in segment_times:
    temp_filename = extract_segment(audio, start_time, end_time)
    
    # Process the temporary file here
    srt_filename = f"{audio_folder_path}{start_time}_{end_time}.srt"
    transcribe_audio(temp_filename,srt_filename)
    srt_files.append(srt_filename)

    # Delete the temporary file when you're done with it - file is still engaged so remove doesnt work / you might want to keep snippets anyway.
    # os.remove(temp_filename)

# Combine the generated SRT files into a single SRT file
full_srt_filename = f"{audio_folder_path}{audio_file_name}.srt"
combine_srt_files(srt_files,full_srt_filename)

# Fix up the SRT file numbering
fix_srt_file(full_srt_filename)
