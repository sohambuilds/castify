import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play, Voice, VoiceSettings 

load_dotenv()

client = ElevenLabs()


custom_voice_settings = VoiceSettings(
    stability=0.71,       
    similarity_boost=0.5, 
    style=0.0,          
    use_speaker_boost=True 
)

audio = client.text_to_speech.convert(
    text = """
<speak>
  The first move is what sets <emphasis level="strong">everything</emphasis> in motion.
  <break time="500ms"/>
  It influences all that follows.
</speak>
""", 
    voice_id="JBFqnCBsd6RMkjVDRZzb", 
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128",
    voice_settings=custom_voice_settings 
)


output_filename = "custom_audio_s71_sb50.mp3"



play(audio)

