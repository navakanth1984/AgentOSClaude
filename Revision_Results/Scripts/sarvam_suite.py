import os
from sarvamai import SarvamAI
import json

client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)

def test_translation():
    print("\n--- Testing Translation (English -> Hindi) ---")
    response = client.text.translate(
        input="May the force be with you.",
        source_language_code="en-IN",
        target_language_code="hi-IN"
    )
    print(f"Input: May the force be with you.")
    print(f"Output: {response.translated_text}")

def test_transliteration():
    print("\n--- Testing Transliteration (Hindi -> Roman Script) ---")
    response = client.text.transliterate(
        input="नमस्ते, आप कैसे हैं?",
        source_language_code="hi-IN",
        target_language_code="en-IN"
    )
    print(f"Input: नमस्ते, आप कैसे हैं?")
    print(f"Output: {response.transliterated_text}")

def test_chat():
    print("\n--- Testing Chat (Sarvam LLM) ---")
    response = client.chat.completions(
        messages=[
            {"role": "user", "content": "What are the top 3 historical places to visit in Hampi?"}
        ]
    )
    print(f"User: What are the top 3 historical places to visit in Hampi?")
    # Chat completions return a response with choices
    if hasattr(response, 'choices') and len(response.choices) > 0:
        print(f"Assistant: {response.choices[0].message.content}")
    else:
        print(f"Raw Response: {response}")

if __name__ == "__main__":
    try:
        test_translation()
        test_transliteration()
        test_chat()
    except Exception as e:
        print(f"An error occurred: {e}")