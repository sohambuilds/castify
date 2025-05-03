import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
DEFAULT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
DEFAULT_MODEL_ID = "eleven_multilingual_v2"
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"
DEFAULT_VOICE_SETTINGS = VoiceSettings(
    stability=0.71,
    similarity_boost=0.5,
    style=0.0,
    use_speaker_boost=True
)

def generate_audio_elevenlabs(
    text,
    voice_id=DEFAULT_VOICE_ID,
    model_id=DEFAULT_MODEL_ID,
    voice_settings=DEFAULT_VOICE_SETTINGS
):
    if not ELEVENLABS_API_KEY:
        print("ELEVENLABS_API_KEY not set in environment.")
        return None
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    try:
        audio_bytes = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            output_format=DEFAULT_OUTPUT_FORMAT,
            voice_settings=voice_settings
        )
        return audio_bytes
    except Exception as e:
        print(f"[ERROR] ElevenLabs audio generation failed: {e}")
        return None
