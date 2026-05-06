#!/usr/bin/env python3
import requests
import json
import time
from pathlib import Path

API_KEY = "paat-b79fDChr4AcTCi4nO0Z5ECx8S4h"
API_BASE = "https://genai-api.picsart.io/v1"

def generate_ai_image(prompt):
    """Generate image via PicsArt AI text-to-image"""
    endpoint = f"{API_BASE}/text2image"

    headers = {
        "X-Picsart-API-Key": API_KEY,
    }

    payload = {
        "prompt": prompt,
        "width": 1920,
        "height": 1080,
        "num_inference_steps": 50,
    }

    print(f"Calling PicsArt AI image generation...")
    print(f"Prompt: {prompt}")

    response = requests.post(endpoint, json=payload, headers=headers)

    if response.status_code not in [200, 202]:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None

    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    # Get inference_id from response
    if "inference_id" in data:
        inference_id = data["inference_id"]
        print(f"Inference ID: {inference_id}")
        print("Polling for result...")

        # Poll for result
        max_retries = 60
        for i in range(max_retries):
            time.sleep(1)
            result = requests.get(
                f"{API_BASE}/text2image/inferences/{inference_id}",
                headers=headers
            )
            result_data = result.json()

            if result_data.get("status") == "success" and "image_url" in result_data:
                image_url = result_data["image_url"]
                print(f"Image ready: {image_url}")

                # Download the image
                img_response = requests.get(image_url)
                if img_response.status_code == 200:
                    output_path = Path(__file__).parent / "hero-background.jpg"
                    with open(output_path, "wb") as f:
                        f.write(img_response.content)
                    print(f"Saved to: {output_path}")
                    return output_path
            elif i % 10 == 0:
                print(f"Still generating... ({i}s elapsed)")

    return None

if __name__ == "__main__":
    prompt = "Futuristic glowing digital AI robots working in a high-tech data center, neon blue and green holographic interface, autonomous agents, sci-fi aesthetic, cinematic lighting"
    generate_ai_image(prompt)
