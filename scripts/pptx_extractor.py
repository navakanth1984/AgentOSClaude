import zipfile
import xml.etree.ElementTree as ET
import sys
import os

def extract_text_from_pptx(path):
    if not os.path.exists(path):
        print(f"Error: {path} does not exist.")
        return

    try:
        with zipfile.ZipFile(path, 'r') as zip_ref:
            # Slides are usually in ppt/slides/slide1.xml, etc.
            slide_files = [f for f in zip_ref.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
            slide_files.sort(key=lambda x: int(x.replace('ppt/slides/slide', '').replace('.xml', '')))

            full_text = []
            for slide_file in slide_files:
                with zip_ref.open(slide_file) as xml_file:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()
                    
                    # Namespaces
                    namespaces = {
                        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                        'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'
                    }
                    
                    slide_num = slide_file.replace('ppt/slides/slide', '').replace('.xml', '')
                    full_text.append(f"\n--- SLIDE {slide_num} ---\n")
                    
                    # Extract all text elements recursively
                    for elem in root.iter():
                        if elem.tag.endswith('}t') and elem.text:
                            full_text.append(elem.text.strip())
            
            return "\n".join(full_text)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    pptx_path = sys.argv[1]
    output_path = sys.argv[2]
    
    text = extract_text_from_pptx(pptx_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Extraction complete. Saved to {output_path}")
