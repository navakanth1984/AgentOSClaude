import os
import requests

def download_file(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {url} to {filename}...")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Successfully saved {filename}")
        else:
            print(f"Failed to download {url}: {response.status_code}")
    else:
        print(f"{filename} already exists.")

if __name__ == "__main__":
    os.makedirs("rust_minar_scene", exist_ok=True)
    # Using verified direct download URLs
    download_file("https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx", "rust_minar_scene/kokoro.onnx")
    download_file("https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin", "rust_minar_scene/voices.bin")
