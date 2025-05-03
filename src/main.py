import os
import re
import io
from pdf_parser.parser import parse_pdf
from rag_system.rag import create_rag_structure
from gemini_api.gemini_client import send_to_gemini
from eli.elevenlabs_client import generate_audio_elevenlabs
from output.generator import generate_final_output
from pydub import AudioSegment

def clean_gemini_output(text):
    if text is None:
        return None
    return text

def parse_speaker_segments(script):
    segments = []
    for line in script.splitlines():
        match = re.match(r'\[(S[12])\]\s*(.+)', line)
        if match:
            speaker, text = match.groups()
            segments.append((speaker, text.strip()))
    return segments

def main(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Error: The file {pdf_path} does not exist.")
        return

    text, metadata = parse_pdf(pdf_path)
    print("PDF parsed successfully.")

    # PLACEHOLDER PROMPT, REPLACE WITH USER PROMPT
    user_prompt = (
        "Write a podcast conversation between two speakers about the main ideas in the document. "
        "Format each line as [S1] or [S2] at the start, alternating between speakers. "
        "Do NOT use SSML tags."
    )

    rag_structure = create_rag_structure(text, prompt=user_prompt)
    print("RAG structure created successfully.")

    gemini_output = send_to_gemini(rag_structure)
    print("Received output from Gemini API.")

    gemini_output_clean = clean_gemini_output(gemini_output)

    # --- Two-speaker audio synthesis ---
    # Define voice IDs for each speaker
    voice_map = {
        "S1": "JBFqnCBsd6RMkjVDRZzb",  # Rachel (example)
        "S2": "EXAVITQu4vr4xnSDxMaL",  # Adam (example)
    }

    segments = parse_speaker_segments(gemini_output_clean)
    audio_segments = []
    for speaker, text in segments:
        voice_id = voice_map.get(speaker, voice_map["S1"])
        audio_bytes = generate_audio_elevenlabs(text, voice_id=voice_id)
        if audio_bytes:
            # If audio_bytes is a generator, convert to bytes
            if hasattr(audio_bytes, '__iter__') and not isinstance(audio_bytes, (bytes, bytearray)):
                audio_bytes = b"".join(audio_bytes)
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
            audio_segments.append(audio_segment)

    if not audio_segments:
        print("Audio generation failed. Exiting.")
        return

    print("Audio generated successfully.")

    # Concatenate all audio segments
    final_audio = audio_segments[0]
    for seg in audio_segments[1:]:
        final_audio += seg

    # Export final audio
    output_filename = "final_output.mp3"
    final_audio.export(output_filename, format="mp3")
    print("Output saved successfully.")

if __name__ == "__main__":
    pdf_file_path = "SR.pdf" # THIS WILL HAVE USER UPLOADED PDF
    main(pdf_file_path)