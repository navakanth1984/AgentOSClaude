import json
from PIL import Image, ImageDraw

def visualize_blocks(json_path, image_path, output_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    for block in data.get('blocks', []):
        coords = block['coordinates']
        shape = [coords['x1'], coords['y1'], coords['x2'], coords['y2']]
        draw.rectangle(shape, outline ="red", width=3)
        draw.text((coords['x1'], coords['y1'] - 10), f"{block['layout_tag']} ({block['reading_order']})", fill="red")
        
    img.save(output_path)
    print(f"Visualization saved to {output_path}")

if __name__ == "__main__":
    # Note: Using the original path provided by user
    img_path = r"C:\Users
avka\OneDrive\Documents\OneDrive\Pictures\6th class 2025 2026\FA3 Revision Dec2025\6 Social 30thDec2025\Social FA2Revision SS26.jpeg"
    json_path = "social_ocr_extracted/metadata/page_001.json"
    visualize_blocks(json_path, img_path, "social_blocks_viz.jpg")
