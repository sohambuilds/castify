import os
from elevenlabs import save

# If you ever import from elevenlabs_integration, update to:
# from eli.elevenlabs_client import ...

def save_audio(output, filename="output.mp3"):
    save(audio=output, filename=filename)
    print(f"Audio saved as '{filename}'")

def format_output(audio_data):
    #PLACHOLDER
    return audio_data

def generate_final_output(audio_data, output_filename="final_output.mp3"):
    formatted_audio = format_output(audio_data)
    save_audio(formatted_audio, output_filename)