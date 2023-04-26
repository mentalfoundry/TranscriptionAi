# TranscriptionAi
 Helps feed files to whisperAI in a free way

# Installation instructions
1. Install ffmpeg as its a key dependency and make sure its added to your environment variables.
2. Restart your machine :)
3. Install missing python dependencies with py -m pip install PACKAGE_NAME 
You will need the following: pydub, openai, load_dotenv, pysrt


# How to use this script
1. Use VLC or similar to convert your .mp4 file into an .mp3
2. Fill in the location fields near the top of the script in trans.py for files less than 20min or use full.py for longer .mp3s

# Additional steps for full.py
1. The output of full.py is one base.srt that is named the same as your audio file and one base_FINAL.srt which contains the proper translation.
The non-final version has dirty data that is sanitised in _FINAL

# For translation it is recommended to still use whisper transcription first and then to do the following.
1. Open the _FINAL file and paste all contents into a .docx file
2. Upload the .docx to https://www.deepl.com/translator/files for processing
3. Download the resulting translation .docx
4. Open and paste its contents into the base.srt and enjoy :)