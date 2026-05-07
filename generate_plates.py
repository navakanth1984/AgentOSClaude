import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompts = {
    "scene1_plate.jpg": "Cinematic wide-angle master shot of a towering asymmetrical brutalist monolith in a high-density urban grid. Atmosphere is a dense amber-tinted mist with floating atmospheric particulates catching the light. Arri Alexa 35mm style.",
    "scene2_plate.jpg": "Medium shot of a South Asian technician. She wears a circular crimson biometric decal on her forehead and a high-gloss iridescent synthetic bodysuit. Intricate cyan-blue bioluminescent tracing pulses beneath her skin. Eyes glowing with intense blue energy. Warm workshop lighting.",
    "scene3_plate.jpg": "Medium wide cinematic shot of a bustling urban market in Zone 4. Two South Asian technicians—one in a reflective suit, one in a rugged technical vest—stand in a crowded alleyway with glowing neon signage in regional scripts. Atmospheric amber haze.",
    "scene4_plate.jpg": "Wide-angle cinematic shot of a central brutalist spire against a sky of descending white-hot energy trails. A large, translucent blue hemispherical energy dome is active in the foreground, projecting a brilliant cyan glow.",
    "scene5_plate.jpg": "High-contrast cinematic portrait of a senior supervisor in high-collar charcoal technical apparel. Sharp features, neutral expression. Background of brutalist concrete walls with sharp geometric shadows. Single intense cyan-blue light source.",
    "scene6_plate.jpg": "Macro cinematic close-up of a translucent fiber-optic conduit connecting two South Asian synthetic beings at the wrist ports. Luminous blue energy pulses through the cable. Warm tungsten workshop lighting with amber mist.",
    "scene7_plate.jpg": "Extreme low-angle tracking shot of a South Asian technician scaling a massive vertical industrial conduit. Towering supply tubes covered in reclaimed metal and glowing data lines. Looking up toward a gargantuan orbital station.",
    "scene8_plate.jpg": "Wide-angle cinematic shot from an orbital tether. A feminine South Asian being stands on the edge, looking at a massive metallic orbital station reflecting in her eyes. Epic scale, deep space background, heavy atmosphere."
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
        with open(filename, 'wb') as handler:
            with open(filename, 'wb') as f:
                f.write(img_data)
        print(f"Successfully saved {filename}")
    except Exception as e:
        print(f"Error generating {filename}: {e}")

if __name__ == "__main__":
    for filename, prompt in prompts.items():
        if not os.path.exists(filename):
            generate_image(filename, prompt)
        else:
            print(f"{filename} already exists, skipping.")
