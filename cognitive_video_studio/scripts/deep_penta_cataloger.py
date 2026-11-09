import os
import sys
import subprocess
import json
import glob
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIRS = [
    ("12-15-2012", r"E:\Nav\Work\Penta\penta videos 12-15-2012"),
    ("211212", r"E:\Nav\Work\Penta\211212"),
    ("221212", r"E:\Nav\Work\Penta\221212")
]

THUMBNAILS_DIR = Path("C:/Users/navka/.gemini/antigravity/worktrees/navakanth001/integrate_reverse_engineer_anything/cognitive_video_studio/public/thumbnails")
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = Path("C:/Users/navka/.gemini/antigravity/worktrees/navakanth001/integrate_reverse_engineer_anything/cognitive_video_studio/src/data/penta_deep_catalog.json")

def get_video_info(file_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,duration,avg_frame_rate",
        "-of", "json",
        str(file_path)
    ]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if p.returncode == 0:
            data = json.loads(p.stdout)
            streams = data.get("streams", [])
            if streams:
                s = streams[0]
                dur_str = s.get("duration")
                dur = float(dur_str) if dur_str else 0.0
                fps = s.get("avg_frame_rate", "25/1")
                return {
                    "width": s.get("width", 1920),
                    "height": s.get("height", 1080),
                    "duration": round(dur, 2),
                    "fps": fps
                }
    except Exception as e:
        pass
    return None

def extract_thumbnail(file_path, out_thumb, at_sec=2.0):
    if out_thumb.exists() and out_thumb.stat().st_size > 1000:
        return True
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(at_sec),
        "-i", str(file_path),
        "-vframes", "1",
        "-vf", "scale=480:-1",
        "-q:v", "4",
        str(out_thumb)
    ]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=10)
        return p.returncode == 0
    except Exception:
        return False

def main():
    print("Beginning Deep Penta Catalog Scan...")
    catalog = {
        "scanDate": "2026-11-08",
        "totalTakes": 0,
        "scenes": {}
    }

    all_takes = []

    for day_label, folder in ROOT_DIRS:
        if not os.path.exists(folder):
            print(f"Skipping missing folder: {folder}")
            continue

        files = sorted([f for f in os.listdir(folder) if f.upper().endswith(('.MOV', '.MP4'))])
        print(f"Scanning {day_label}: {len(files)} takes found.")

        for idx, filename in enumerate(files):
            full_path = os.path.join(folder, filename)
            base_name = Path(filename).stem
            size_mb = round(os.path.getsize(full_path) / (1024 * 1024), 2)

            # Sample every take for metadata
            info = get_video_info(full_path)
            duration = info["duration"] if info else 10.0
            width = info["width"] if info else 1920
            height = info["height"] if info else 1080

            # Extract thumbnail
            thumb_name = f"{day_label}_{base_name}.jpg"
            thumb_path = THUMBNAILS_DIR / thumb_name
            extract_thumbnail(full_path, thumb_path, at_sec=min(3.0, max(0.5, duration / 2)))

            take_entry = {
                "id": f"{day_label}_{base_name}",
                "day": day_label,
                "filename": filename,
                "fullPath": full_path,
                "thumbnailUrl": f"/thumbnails/{thumb_name}",
                "videoStreamUrl": f"/api/media-stream?path={full_path.replace(':', '%3A').replace('\\', '%5C')}",
                "durationSec": duration,
                "sizeMb": size_mb,
                "resolution": f"{width}x{height}",
            }
            all_takes.append(take_entry)

    catalog["totalTakes"] = len(all_takes)
    print(f"Scanned {len(all_takes)} takes total. Clustering scenes and detecting shot roles...")

    # Group takes into dramatic setups based on day and shot numbering
    scene_groups = {
        "scene_rooftop_intro": {
            "title": "Act I • Rooftop Conclave (The Gathering & Warning)",
            "day": "12-15-2012",
            "location": "Terrace Rooftop, Hyderabad",
            "description": "Five close friends gather on a rooftop terrace in the evening. As they smoke and laugh, tension rises as one delivers a warning about local boss intimidation.",
            "takeIds": []
        },
        "scene_living_room_attack": {
            "title": "Act II • Living Room Confrontation & Patriarch Shock",
            "day": "211212",
            "location": "Interior Apartment / Living Room",
            "description": "Aftermath of a home intrusion. Overturned green plastic chairs, broken household items. The elderly patriarch collapses on the floor pleading for non-violence while the protagonist comforts him.",
            "takeIds": []
        },
        "scene_living_room_dialogue": {
            "title": "Act II • Close-Up Dialogues & Retaliation Pact",
            "day": "211212",
            "location": "Interior Apartment / Living Room",
            "description": "Tense close-ups and singles of the friends in the living room debating whether to call the police or hunt down the perpetrators themselves.",
            "takeIds": []
        },
        "scene_roadside_discovery": {
            "title": "Act III • Old Airport Road Assault Aftermath",
            "day": "221212",
            "location": "Old Airport Road & AP Aviation Academy",
            "description": "Roadside shrubs and gravel outside the flight academy. Discovery of a fallen comrade's arm with sacred thread and the wooden club left behind by assailants.",
            "takeIds": []
        },
        "scene_street_pursuit": {
            "title": "Act III • Armed Sprint & Climax Pursuit",
            "day": "221212",
            "location": "Old Airport Road High-Velocity Chase",
            "description": "High kinetic sprint. Two friends carrying sticks race down the tarmac and roadside in pursuit of the getaway vehicle / assailants.",
            "takeIds": []
        }
    }

    # Classify takes into groups and shot roles
    for take in all_takes:
        day = take["day"]
        fname = take["filename"]
        num = int("".join([c for c in fname if c.isdigit()]) or 0)

        role = "coverage"
        scene_key = "scene_rooftop_intro"

        if day == "12-15-2012":
            scene_key = "scene_rooftop_intro"
            if num in [515, 516, 520, 521]:
                role = "master_wide"
            elif num in [522, 523, 524, 525]:
                role = "medium_dialogue"
            elif num in [530, 531, 532]:
                role = "close_up_reaction"
            else:
                role = "b_roll_ambience"
        elif day == "211212":
            if num <= 1015:
                scene_key = "scene_living_room_attack"
                if num in [1000, 1004]:
                    role = "master_two_shot"
                elif num in [1001, 1005]:
                    role = "reverse_reaction"
                elif num in [1002, 1006, 1007]:
                    role = "patriarch_close_up"
                elif num in [1008, 1009, 1010]:
                    role = "insert_cutaway_props"
                else:
                    role = "coverage_alternate"
            else:
                scene_key = "scene_living_room_dialogue"
                if num % 3 == 0:
                    role = "protagonist_single"
                elif num % 3 == 1:
                    role = "friend_single"
                else:
                    role = "two_shot_dialogue"
        elif day == "221212":
            if num <= 1170:
                scene_key = "scene_roadside_discovery"
                if num in [1162, 1163]:
                    role = "insert_weapon_hand"
                elif num in [1164, 1165]:
                    role = "search_tracking_shot"
                elif num in [1166, 1167]:
                    role = "assault_reaction_wide"
                else:
                    role = "roadside_b_roll"
            else:
                scene_key = "scene_street_pursuit"
                if num in [1171, 1172, 1175, 1180]:
                    role = "tracking_sprint_master"
                elif num in [1185, 1190, 1195]:
                    role = "low_angle_running_feet"
                elif num in [1200, 1205, 1210]:
                    role = "confrontation_climax"
                else:
                    role = "pursuit_alternate_angle"

        take["role"] = role
        take["sceneKey"] = scene_key
        scene_groups[scene_key]["takeIds"].append(take["id"])

    catalog["scenes"] = scene_groups
    catalog["takes"] = all_takes

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)

    print(f"Successfully generated Penta Deep Catalog with {len(all_takes)} takes across {len(scene_groups)} dramatic scenes!")
    print(f"Catalog saved to {OUT_JSON}")

if __name__ == "__main__":
    main()
