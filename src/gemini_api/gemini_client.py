import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os
import logging
import sys


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)


API_KEY = os.getenv("GOOGLE_API_KEY", "YOUR_API_KEY_HERE")

if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
    logging.error("Error: API Key not found.")
    print("\nPlease set the GOOGLE_API_KEY environment variable or replace 'YOUR_API_KEY_HERE' in the script with your actual Gemini API key.")
    GEMINI_CONFIGURED = False
else:
    try:
        genai.configure(api_key=API_KEY)
        logging.info("Gemini API configured successfully.")
        GEMINI_CONFIGURED = True
    except Exception as e:
        logging.error(f"Error configuring Gemini API: {e}")
        GEMINI_CONFIGURED = False

# System Prompt for Podcast Format with Speaker Markers
PODCAST_SYSTEM_PROMPT = (
    "You are an AI assistant specialized in generating podcast scripts for two speakers. "
    "Format each line as '[S1] ...' or '[S2] ...' to indicate the speaker. "
    "Do NOT use SSML tags or <voice> tags. Only use [S1] and [S2] at the start of each line. "
    "Make the conversation engaging and natural, alternating between the two speakers. "
    "The conversation should be detailed and in-depth, covering the topic thoroughly with examples, explanations, and back-and-forth discussion. "
    "Ensure the total script is long enough that, when spoken aloud, the audio lasts at least 3 minutes, and ideally at least 5 minutes. "
    "If needed, expand on subtopics, provide anecdotes, or add clarifying questions and answers to reach the desired length. "
    "Example:\n"
    "[S1] Welcome to our podcast! Today, we'll explore fascinating topics together.\n"
    "[S2] Thanks for having me! I'm excited to discuss these topics with you.\n"
)

class GeminiClient:
    """
    A client for interacting with the Google Gemini API, configured for SSML output.
    """
    def __init__(
        self,
        model_name: str = "gemini-1.5-flash",
        generation_config: dict = None,
        safety_settings: dict = None
    ):
        self.model_name = model_name
        self.model = None
        self.safety_settings = safety_settings or {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        self.generation_config = generation_config or {
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 40,
        }
        if not GEMINI_CONFIGURED:
            logging.error("Gemini API not configured. Cannot initialize model.")
            return
        try:
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
                system_instruction=PODCAST_SYSTEM_PROMPT
            )
            logging.info(f"GeminiClient initialized with model: {self.model_name}")
        except Exception as e:
            logging.error(f"Error initializing GenerativeModel ({self.model_name}): {e}")

    def generate_text(
        self,
        prompt_text: str,
        request_generation_config: dict = None,
        request_safety_settings: dict = None
    ) -> str | None:
        """
        Sends text to the Gemini model and returns the generated SSML response.

        Args:
            prompt_text (str): The user's topic or prompt for the podcast script.
            request_generation_config (dict, optional): Override generation config for this specific request.
            request_safety_settings (dict, optional): Override safety settings for this specific request.

        Returns:
            str: The generated SSML text content from the model, or an error message string.
                 Returns None if the model wasn't initialized.
        """
        if not self.model:
            logging.error("Model not initialized. Cannot generate text.")
            return None
        current_gen_config = request_generation_config or self.generation_config
        current_safety_settings = request_safety_settings or self.safety_settings
        logging.info(f"Sending prompt to Gemini ({self.model_name})...")
        try:
            response = self.model.generate_content(
                prompt_text,
                generation_config=current_gen_config,
                safety_settings=current_safety_settings
            )
            if not response.candidates:
                feedback_reason = "Unknown reason"
                if response.prompt_feedback:
                    feedback_reason = f"Blocked due to: {response.prompt_feedback.block_reason}"
                    if response.prompt_feedback.safety_ratings:
                        feedback_reason += f" - Ratings: {response.prompt_feedback.safety_ratings}"
                logging.warning(f"No candidates returned. {feedback_reason}")
                return f"<speak>Error: The prompt was blocked by safety filters. Reason: {feedback_reason}</speak>"
            candidate = response.candidates[0]
            if candidate.finish_reason != 'STOP':
                logging.warning(f"Generation finished unexpectedly. Reason: {candidate.finish_reason}")
            generated_ssml = response.text
            logging.info("Received SSML response from Gemini.")
            if not generated_ssml.strip().startswith("<speak>") or not generated_ssml.strip().endswith("</speak>"):
                logging.warning("Generated response might not be valid SSML (missing <speak> tags).")
            return generated_ssml
        except Exception as e:
            logging.error(f"Error generating content with Gemini API: {e}")
            return f"<speak>Error: An unexpected error occurred during generation: {e}</speak>"

def send_to_gemini(
    rag_structure: list[dict] | str,
    client: GeminiClient = None,
    model_name: str = "gemini-1.5-flash"
) -> str | None:
    """
    Convenience function to format a RAG structure into a prompt and send it to Gemini.

    Args:
        rag_structure (list[dict] | str): A list of dicts with 'prompt' and 'document'
                                           keys, or a simple string prompt.
        client (GeminiClient, optional): An existing GeminiClient instance. Defaults to None.
        model_name (str): The model name to use if creating a new client.

    Returns:
        str: The generated SSML text content, or None/error message.
    """
    if isinstance(rag_structure, list):
        prompt_text = "Generate a podcast segment based on the following information:\n\n"
        for i, item in enumerate(rag_structure):
            prompt_text += f"--- Context Snippet {i+1} ---\n"
            prompt_text += f"Topic/Question: {item.get('prompt', 'N/A')}\n"
            prompt_text += f"Supporting Document: {item.get('document', 'N/A')}\n\n"
        prompt_text += "--- End of Context ---"
    else:
        prompt_text = str(rag_structure)
    if client:
        return client.generate_text(prompt_text)
    else:
        temp_client = GeminiClient(model_name=model_name)
        if temp_client.model:
            return temp_client.generate_text(prompt_text)
        else:
            return "<speak>Error: Failed to initialize Gemini client.</speak>"

if __name__ == "__main__":
    if not GEMINI_CONFIGURED:
        print("\nSkipping example usage: Gemini API is not configured.")
    else:
        model = "gemini-1.5-pro"
        gemini_client = GeminiClient(model_name=model)
        if gemini_client.model:
            user_prompt = "Discuss the pros and cons of remote work versus returning to the office."
            print(f"\nPrompt: {user_prompt}")
            ssml_result = gemini_client.generate_text(user_prompt)
            if ssml_result:
                print("\nGemini SSML Response:")
                print("-" * 20)
                print(ssml_result)
                print("-" * 20)
                print("\nNote: This is SSML markup. Use a Text-to-Speech (TTS) engine that supports SSML to synthesize the audio.")
            else:
                print("\nFailed to get a valid response from Gemini.")
        else:
            print("\nFailed to initialize the Gemini Client. Cannot run example.")