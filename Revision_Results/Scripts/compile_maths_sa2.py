import json
import os

def compile_maths_sa2_results():
    metadata_dir = "maths_sa2_extracted/metadata"
    files = sorted([f for f in os.listdir(metadata_dir) if f.endswith('.json')])
    
    full_text = "MATHS SA2 REVISION - FULL SET\n" + "="*30 + "\n\n"
    
    for filename in files:
        page_num = filename.split('_')[1].split('.')[0]
        full_text += f"--- PAGE {page_num} ---\n"
        
        with open(os.path.join(metadata_dir, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)
            blocks = data.get('blocks', [])
            blocks.sort(key=lambda x: x.get('reading_order', 0))
            
            for block in blocks:
                if block.get('layout_tag') in ['paragraph', 'header', 'list_item', 'table']:
                    text = block.get('text', '').strip()
                    if text:
                        full_text += text + "\n\n"
        
        full_text += "-"*20 + "\n\n"
        
    with open("Full_Maths_SA2_Revision_Extract.txt", "w", encoding="utf-8") as f:
        f.write(full_text)
    print("Compiled full text to Full_Maths_SA2_Revision_Extract.txt")

if __name__ == "__main__":
    compile_maths_sa2_results()