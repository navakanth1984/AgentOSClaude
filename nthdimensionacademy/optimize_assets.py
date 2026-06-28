import os
import sys
from PIL import Image

# Verify and try importing pillow-avif-plugin if available
avif_supported = False
try:
    import pillow_avif
    avif_supported = True
    print("[Optimize] AVIF encoding support verified via pillow-avif-plugin.")
except ImportError:
    print("[Optimize] WARNING: pillow-avif-plugin not found. AVIF support will be bypassed.")
    print("           Falling back to WebP and optimized JPEGs/PNGs.")

# Source and Target directories
REACT_ASSETS_DIR = r"c:\Users\navka\navakanth001\nth-dimension-react\public\assets"
VANILLA_ASSETS_DIR = r"c:\Users\navka\navakanth001\nthdimensionacademy\assets"
VANILLA_ROOT_DIR = r"c:\Users\navka\navakanth001\nthdimensionacademy"

# Target widths for responsive images
RESPONSIVE_WIDTHS = [480, 768, 1200, 1600, 2400]

def optimize_image(src_path, dest_dir, base_name):
    """
    Optimizes a single image:
    1. Resizes it to responsive widths.
    2. Converts to WebP.
    3. Converts to AVIF (if supported).
    4. Compresses original format.
    """
    os.makedirs(dest_dir, exist_ok=True)
    
    try:
        with Image.open(src_path) as img:
            # Determine image format
            original_format = img.format if img.format else "JPEG"
            print(f"\nProcessing: {src_path} (Format: {original_format}, Size: {os.path.getsize(src_path) / 1024 / 1024:.2f} MB)")
            
            # --- 1. Compress Original Format ---
            ext = "." + original_format.lower()
            if ext == ".jpeg":
                ext = ".jpg"
            dest_orig_path = os.path.join(dest_dir, f"{base_name}{ext}")
            img.save(dest_orig_path, original_format, quality=82, optimize=True)
            print(f"  -> Compressed {original_format}: {os.path.getsize(dest_orig_path) / 1024:.1f} KB")

            # --- 2. Convert to WebP (Full resolution) ---
            dest_webp_path = os.path.join(dest_dir, f"{base_name}.webp")
            img.save(dest_webp_path, "WEBP", quality=80)
            print(f"  -> Converted to WebP: {os.path.getsize(dest_webp_path) / 1024:.1f} KB")

            # --- 3. Convert to AVIF (Full resolution) ---
            if avif_supported:
                try:
                    dest_avif_path = os.path.join(dest_dir, f"{base_name}.avif")
                    img.save(dest_avif_path, "AVIF", speed=6, quality=65)
                    print(f"  -> Converted to AVIF: {os.path.getsize(dest_avif_path) / 1024:.1f} KB")
                except Exception as e:
                    print(f"  -> Failed to write AVIF: {e}")

            # --- 4. Generate Responsive Widths ---
            # Avoid upscaling: only generate sizes smaller than the original width
            orig_width, orig_height = img.size
            for width in RESPONSIVE_WIDTHS:
                if width < orig_width:
                    aspect_ratio = orig_height / orig_width
                    height = int(width * aspect_ratio)
                    resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
                    
                    # WebP responsive
                    resp_webp_path = os.path.join(dest_dir, f"{base_name}-{width}w.webp")
                    resized_img.save(resp_webp_path, "WEBP", quality=75)
                    
                    # AVIF responsive
                    if avif_supported:
                        try:
                            resp_avif_path = os.path.join(dest_dir, f"{base_name}-{width}w.avif")
                            resized_img.save(resp_avif_path, "AVIF", speed=7, quality=60)
                        except Exception:
                            pass
                            
                    print(f"     * Generated {width}w responsive sizes")
                    
    except Exception as e:
        print(f"ERROR processing {src_path}: {e}")

def main():
    # 1. Optimize the huge images inside vanilla root / public assets
    targets = [
        # Vanilla root JPEGs
        {"src": os.path.join(VANILLA_ROOT_DIR, "[IMAGE_END]__A_10-row_vertical_grid_202605060728.jpeg"), "base": "grid_bg"},
        {"src": os.path.join(VANILLA_ROOT_DIR, "[IMAGE_END]__A_premium_4D_glass_202605052049.jpeg"), "base": "glass_bg"},
        # React public assets copies
        {"src": os.path.join(REACT_ASSETS_DIR, "[IMAGE_END]__A_10-row_vertical_grid_202605060728.jpeg"), "base": "grid_bg"},
        {"src": os.path.join(REACT_ASSETS_DIR, "[IMAGE_END]__A_premium_4D_glass_202605052049.jpeg"), "base": "glass_bg"},
        # Logo target
        {"src": os.path.join(REACT_ASSETS_DIR, "logo_gold.jpeg"), "base": "logo_gold"},
        # Instructor profiles / badges
        {"src": os.path.join(REACT_ASSETS_DIR, "media__1777541920144.jpg"), "base": "profile_mct"},
        {"src": os.path.join(REACT_ASSETS_DIR, "media__1777541920190.jpg"), "base": "badge_mct_small"},
        {"src": os.path.join(REACT_ASSETS_DIR, "media__1777542950074.jpg"), "base": "badge_mct_hero"},
    ]
    
    # Process each target
    for target in targets:
        if os.path.exists(target["src"]):
            # Optimize to React public/assets
            optimize_image(target["src"], REACT_ASSETS_DIR, target["base"])
            # Optimize to Vanilla assets/
            optimize_image(target["src"], VANILLA_ASSETS_DIR, target["base"])
        else:
            print(f"Skipping (not found): {target['src']}")

    # Copy files like videos directly from React public/assets to Vanilla assets if they exist
    print("\nCopying other media assets (videos/PNGs) for vanilla site standalone deployment...")
    os.makedirs(VANILLA_ASSETS_DIR, exist_ok=True)
    media_extensions = [".mp4", ".png"]
    for file_name in os.listdir(REACT_ASSETS_DIR):
        ext = os.path.splitext(file_name)[1].lower()
        if ext in media_extensions:
            src_path = os.path.join(REACT_ASSETS_DIR, file_name)
            dest_path = os.path.join(VANILLA_ASSETS_DIR, file_name)
            if not os.path.exists(dest_path):
                try:
                    import shutil
                    shutil.copy2(src_path, dest_path)
                    print(f"  -> Copied {file_name}")
                except Exception as e:
                    print(f"  -> Failed to copy {file_name}: {e}")

    print("\nImage asset optimization sequence completed successfully!")

if __name__ == "__main__":
    main()
