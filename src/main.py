import os
from pdf_parser.parser import parse_pdf
from rag_system.rag import create_rag_structure
from gemini_api.gemini_client import send_to_gemini
from elevenlabs_integration.elevenlabs_client import generate_audio_elevenlabs
from output.generator import generate_final_output

def clean_gemini_output(text):
   
    if text is None:
        return None
    idx = text.find("<speak>")
    if idx != -1:
        return text[idx:]
    return text

def main(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Error: The file {pdf_path} does not exist.")
        return

 
    text, metadata = parse_pdf(pdf_path)
    print("PDF parsed successfully.")

    # PLACEHOLDER PROMPT, REPLACE WITH USER PROMPT
    user_prompt = "Summarize the document as an engaging podcast episode for a general audience."

    rag_structure = create_rag_structure(text, prompt=user_prompt)
    print("RAG structure created successfully.")

 
    gemini_output = send_to_gemini(rag_structure)
    print("Received output from Gemini API.")

    
    gemini_output_clean = clean_gemini_output(gemini_output)

    
    audio_output = generate_audio_elevenlabs(gemini_output_clean)
    if audio_output is None:
        print("Audio generation failed. Exiting.")
        return
    print("Audio generated successfully.")

 
    generate_final_output(audio_output)
    print("Output saved successfully.")

if __name__ == "__main__":
    pdf_file_path = "SR.pdf" # THIS WILL HAVE USER UPLOADED PDF
    main(pdf_file_path)