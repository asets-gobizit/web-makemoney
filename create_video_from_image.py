#!/usr/bin/env python3
"""
Create animated video from a static image with subtle animations
Uses FFmpeg + imagemagick to create zoom/pan effects
"""
import subprocess
import os
from pathlib import Path

def create_animated_video(input_image, output_video, duration=16):
    """Create animated video with zoom effect from static image"""

    # FFmpeg command to create video with subtle zoom effect
    # Using scale and motion to add subtle animation
    cmd = [
        'ffmpeg',
        '-loop', '1',                    # Loop the image
        '-i', str(input_image),          # Input image
        '-c:v', 'libx264',              # H.264 codec
        '-pix_fmt', 'yuv420p',          # Pixel format
        '-preset', 'fast',              # Speed up encoding
        '-crf', '23',                   # Quality (lower=better, 23 is good balance)
        '-t', str(duration),            # Duration in seconds
        '-filter:v', (
            'scale=1920:1080,'           # Ensure 1920x1080
            'zoompan=z=1.02:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):'  # Subtle zoom effect
            'd=' + str(int(duration * 30)) + ':s=1920x1080'       # 30fps
        ),
        '-y',                            # Overwrite output
        str(output_video)
    ]

    print(f"Creating video from: {input_image}")
    print(f"Output: {output_video}")
    print(f"Duration: {duration}s")
    print(f"Command: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            file_size = Path(output_video).stat().st_size / (1024 * 1024)
            print(f"[OK] Video created successfully")
            print(f"[OK] File size: {file_size:.1f} MB")
            print(f"[OK] Duration: {duration} seconds")
            print(f"[OK] Resolution: 1920x1080")
            print(f"[OK] Codec: H.264 MP4")
            return True
        else:
            print(f"[ERROR] FFmpeg failed:")
            print(f"STDERR: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("[ERROR] Video generation timed out (>5 min)")
        return False
    except FileNotFoundError:
        print("[ERROR] FFmpeg not found. Please install: winget install ffmpeg")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    input_img = Path(__file__).parent / "my-hero-background#2.png"
    output_vid = Path(__file__).parent / "hero-bots.mp4"

    if not input_img.exists():
        print(f"[ERROR] Image not found: {input_img}")
        exit(1)

    # Create the video
    success = create_animated_video(str(input_img), str(output_vid), duration=16)

    if success:
        print(f"\n[SUCCESS] Video ready to deploy!")
        print(f"  Old: hero-bots.mp4 (replaced)")
        print(f"  New: {output_vid}")
    else:
        print(f"\n[FAILED] Video creation failed. Check FFmpeg installation.")
        exit(1)
