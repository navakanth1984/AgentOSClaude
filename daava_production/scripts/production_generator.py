import os
import json
import re
from pathlib import Path
from observation_engine import ObservationEngine

engine = ObservationEngine()

def load_dna(dna_path):
    """Loads a Visual DNA JSON file."""
    try:
        with open(dna_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading DNA at {dna_path}: {e}")
        return None

def extract_dna_vars(dna_data):
    """Flattens DNA data into simple prompt-ready strings."""
    if not dna_data:
        return {}
    
    char = dna_data.get('character', {})
    apparel = char.get('apparel', {})
    
    def get_color(obj):
        if isinstance(obj, dict):
            return obj.get('hex', '#UNKNOWN')
        return obj

    # Observation: Check for missing data (Context Friction)
    missing = []
    if not apparel.get('base_suit'): missing.append('base_suit')
    if not apparel.get('harness'): missing.append('harness')
    if not apparel.get('helmet'): missing.append('helmet')
    
    if missing:
        engine.log_trace("CONTEXT_FRICTION", {
            "reason": f"Missing DNA fields: {', '.join(missing)}",
            "source": "climber_dna.json"
        })

    return {
        'suit_color': get_color(apparel.get('base_suit', {}).get('color', '#FF8C00')),
        'harness_color': get_color(apparel.get('harness', {}).get('color', '#2F4F4F')),
        'helmet_color': get_color(apparel.get('helmet', {}).get('color', '#FFD700')),
        'physique': char.get('physique', 'Athletic build'),
        'lighting': dna_data.get('scene_context', {}).get('lighting', {}).get('primary', 'Cinematic lighting')
    }

def parse_screenplay(file_path):
    """Parses a screenplay and identifies shot prompts and DNA anchors."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Find DNA Anchor
    dna_match = re.search(r'Character Anchor:.*?\(DNA:\s*(.*?)\)', content)
    dna_id = dna_match.group(1) if dna_match else None

    # Split by shots or generate them
    # For now, we look for [SHOT X - SEEDANCE PROMPT] blocks
    shots = re.findall(r'\[SHOT (\d+) - SEEDANCE PROMPT\]\n(.*?)(?=\n\n|---|$)', content, re.DOTALL)
    
    return dna_id, shots

def generate_production_prompts(screenplay_path, dna_folder):
    """Generates the final Seedance/Higgsfield production prompts."""
    dna_id, shots = parse_screenplay(screenplay_path)
    
    if not dna_id:
        print("No DNA anchor found in screenplay.")
        return

    dna_file = "climber_dna.json" # Hardcoded for now
    dna_path = Path(dna_folder) / dna_file
    dna_data = load_dna(dna_path)
    dna_vars = extract_dna_vars(dna_data)

    print(f"--- PRODUCTION GENERATOR ---")
    print(f"Project: DAAVA")
    print(f"Source: {os.path.basename(screenplay_path)}")
    print(f"DNA Anchor: {dna_id}")
    print(f"----------------------------\n")

    for shot_num, prompt in shots:
        # Surgical Injection & Drift Correction
        refined_prompt = prompt.strip()
        
        # Correct common legacy/default drift
        refined_prompt = refined_prompt.replace("#FF8C00", dna_vars['suit_color'])
        refined_prompt = refined_prompt.replace("#2F4F4F", dna_vars['harness_color'])
        refined_prompt = refined_prompt.replace("#FFD700", dna_vars['helmet_color'])

        # Ensure lens and lighting are explicitly injected if missing
        if "14mm" not in refined_prompt:
            refined_prompt += f" 14mm focal length."
        if "Worm's-Eye View" not in refined_prompt and "low angle" in refined_prompt.lower():
            refined_prompt = refined_prompt.replace("low angle", "Worm's-Eye View (Extreme Low)")

        # Ensure DNA consistency is explicitly restated for the model
        dna_block = f"\n\n[SURGICAL DNA LOCK]:\n- Character Physique: {dna_vars['physique']}\n- Base Suit Hex: {dna_vars['suit_color']}\n- Harness Hex: {dna_vars['harness_color']}\n- Helmet Hex: {dna_vars['helmet_color']}"
        
        full_production_prompt = refined_prompt + dna_block
        
        print(f"SHOT {shot_num} PRODUCTION PROMPT:")
        print(full_production_prompt)
        print("-" * 30)
        
        output_file = Path(screenplay_path).parent / f"shot_{shot_num}_production.txt"
        with open(output_file, 'w') as f:
            f.write(full_production_prompt)
        
        # Log generation trace
        engine.log_trace("GENERATION_SUCCESS", {
            "shot_num": shot_num,
            "output_file": str(output_file),
            "dna_anchor": dna_id
        })
        
        print(f"Saved to: {output_file}\n")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    screenplay = os.path.join(script_dir, "chapter1_cyber_nampally.md")
    dna_dir = os.path.join(os.path.dirname(script_dir), "dna")
    
    generate_production_prompts(screenplay, dna_dir)
