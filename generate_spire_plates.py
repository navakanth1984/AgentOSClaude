import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompts = {
    "rust_minar_scene/evolved_plate_A_wide.jpg": "Cinematic 35mm film shot, ARRI ALEXA aesthetic. Wide-angle establishing shot of an Ancient Weathered Spire in a swirling dark mist void. Shadow Cut volumetric god rays cutting through the atmosphere. The spire's impossible height pierces the abyss. High-contrast, sharp detail, photorealistic, cinematic scale.",
    "rust_minar_scene/evolved_plate_B_macro.jpg": "Macro photography, 35mm lens. Close-up of oxidized bronze verdigris edges and deep fissures on an ancient spire. Rembrandt Lighting catching the sharp metallic ridges against a pitch-black abyss. Anamorphic lens flare glints. Extreme high detail, professional color grading, film grain."
}

def generate_image(filename, prompt):
    print(f"Generating {filename}...")
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            n=1,
        )
        image_url = response.data[0].url
        img_data = requests.get(image_url).content
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'wb') as f:
            f.write(img_data)
            
        print(f"Successfully saved {filename}")
    except Exception as e:
        print(f"Error generating {filename}: {e}")

if __name__ == "__main__":
    for filename, prompt in prompts.items():
        generate_image(filename, prompt)
