import os
from sarvamai import SarvamAI

client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)

def test_telugu_translation():
    print("")
    print("--- Testing Translation (English -> Telugu) ---")
    en_text = "How are you doing today?"
    response_en_te = client.text.translate(
        input=en_text,
        source_language_code="en-IN",
        target_language_code="te-IN"
    )
    print(f"English: {en_text}")
    print(f"Telugu: {response_en_te.translated_text}")

    print("")
    print("--- Testing Translation (Telugu -> English) ---")
    te_text = response_en_te.translated_text
    response_te_en = client.text.translate(
        input=te_text,
        source_language_code="te-IN",
        target_language_code="en-IN"
    )
    print(f"Telugu: {te_text}")
    print(f"English: {response_te_en.translated_text}")

def test_telugu_transliteration():
    print("")
    print("--- Testing Transliteration (Telugu -> Roman Script) ---")
    te_text = "నమస్కారం, మీరు ఎలా ఉన్నారు?"
    response = client.text.transliterate(
        input=te_text,
        source_language_code="te-IN",
        target_language_code="en-IN"
    )
    print(f"Telugu: {te_text}")
    print(f"Roman: {response.transliterated_text}")

if __name__ == "__main__":
    try:
        test_telugu_translation()
        test_telugu_transliteration()
    except Exception as e:
        print(f"An error occurred: {e}")