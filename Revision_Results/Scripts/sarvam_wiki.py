import os
from sarvamai import SarvamAI

client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)

def test_regular_chat():
    print("")
    print("--- Testing Regular Chat (No Grounding) ---")
    query = "Who was the ruler of the Vijayanagara Empire during its golden age?"
    
    print(f"User: {query}")

    try:
        response = client.chat.completions(
            messages=[
                {"role": "user", "content": query}
            ]
        )

        if hasattr(response, 'choices') and len(response.choices) > 0:
            print(f"Assistant: {response.choices[0].message.content}")
        else:
            print(f"Raw Response: {response}")
            
    except Exception as e:
        print(f"Error during regular chat: {e}")

if __name__ == "__main__":
    test_regular_chat()