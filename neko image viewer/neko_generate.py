import sys
import os
import requests
import urllib.parse
import time
from neko_viewer import show_image  # your existing viewer

def generate_image_url(prompt):
    base_url = "https://image.pollinations.ai/prompt/"
    prompt_encoded = urllib.parse.quote(prompt)
    return base_url + prompt_encoded

def download_image(url, save_path):
    print("⬇️ Downloading generated image...")
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print("✅ Image saved to", save_path)
        return True
    else:
        print(f"❌ Failed to download image, status code {r.status_code}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: neko_generate.py \"your prompt here\"")
        sys.exit(1)

    prompt = ' '.join(sys.argv[1:])
    output_dir = "generated"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = int(time.time())
    filename = os.path.join(output_dir, f"generated_{timestamp}.png")

    print("🎨 Generating image for prompt:", prompt)
    image_url = generate_image_url(prompt)

    if download_image(image_url, filename):
        show_image(filename)

if __name__ == "__main__":
    main()
