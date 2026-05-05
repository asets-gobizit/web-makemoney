#!/usr/bin/env python3
"""
Generate AI Bots + Code hero video using PIL frames + FFmpeg.
Creates frames, then encodes to MP4.
"""

import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import os

def create_frame(frame_num, total_frames, fps=30):
    """Create a single frame with animated bots + code."""

    width, height = 1920, 1080
    img = Image.new('RGB', (width, height), color='#051020')
    draw = ImageDraw.Draw(img, 'RGBA')

    # Time in seconds
    t = frame_num / fps

    # Try to load monospace font, fallback to default
    try:
        code_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 56)
        big_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 96)
    except:
        code_font = ImageFont.load_default()
        big_font = ImageFont.load_default()

    # Dark background gradient effect (simple)
    for y in range(0, height, 10):
        alpha = int(255 * (1 - y / height * 0.3))
        draw.rectangle([(0, y), (width, y+10)], fill=(5, 16, 32, alpha))

    # Animated code lines (typewriter effect)
    code_lines = [
        ("const bot = new AIAgent();", 200, (0, 217, 255), 0.5, 3),
        ("bot.execute(task, autonomously=true);", 300, (16, 185, 129), 1.5, 4),
        ("revenue = await bot.earnings();", 400, (255, 215, 0), 2.5, 5),
    ]

    for text, y_pos, color, fade_start, fade_end in code_lines:
        alpha = 255
        if t < fade_start:
            alpha = int(255 * (t / fade_start))
        elif t > fade_end:
            alpha = int(255 * max(0, 1 - (t - fade_end) / 2))

        if alpha > 0:
            # Draw text with glow effect
            for offset in range(1, 5):
                draw.text((width//2 - 300, y_pos - offset), text,
                         font=code_font, fill=(*color, alpha // 4))
            draw.text((width//2 - 300, y_pos), text,
                     font=code_font, fill=(*color, alpha))

    # Animated revenue counter
    if t > 3:
        counter_alpha = min(255, int(255 * (t - 3) / 2))
        revenue = min(10000, int(10000 * (t - 3) / 5))
        revenue_text = f"${revenue:,}"

        if counter_alpha > 0:
            draw.text((width//2 - 150, 500), revenue_text,
                     font=big_font, fill=(16, 185, 129, counter_alpha))

    # Animated bot circles (pulsing nodes)
    bot_left_x = width // 4
    bot_right_x = 3 * width // 4
    bot_y = 150

    # Left bot (cyan)
    pulse = 100 + 80 * math.sin(2 * math.pi * t / 3)
    draw.ellipse(
        [(bot_left_x - pulse//2, bot_y - pulse//2),
         (bot_left_x + pulse//2, bot_y + pulse//2)],
        outline=(0, 217, 255, 150),
        width=3
    )
    draw.ellipse(
        [(bot_left_x - 40, bot_y - 40),
         (bot_left_x + 40, bot_y + 40)],
        fill=(30, 64, 175, 200)
    )

    # Right bot (green)
    pulse2 = 100 + 80 * math.cos(2 * math.pi * t / 3)
    draw.ellipse(
        [(bot_right_x - pulse2//2, bot_y - pulse2//2),
         (bot_right_x + pulse2//2, bot_y + pulse2//2)],
        outline=(16, 185, 129, 150),
        width=3
    )
    draw.ellipse(
        [(bot_right_x - 40, bot_y - 40),
         (bot_right_x + 40, bot_y + 40)],
        fill=(30, 64, 175, 200)
    )

    # Connecting line between bots (animated)
    line_alpha = int(255 * (0.5 + 0.5 * math.sin(2 * math.pi * t / 2)))
    draw.line(
        [(bot_left_x, bot_y), (bot_right_x, bot_y)],
        fill=(0, 217, 255, line_alpha),
        width=3
    )

    # Data flow indicators (small moving dots)
    flow_pos = (bot_left_x + (bot_right_x - bot_left_x) * ((t % 2) / 2))
    draw.ellipse(
        [(flow_pos - 8, bot_y - 8), (flow_pos + 8, bot_y + 8)],
        fill=(255, 215, 0, 200)
    )

    return img

def generate_video():
    """Generate MP4 video from frames."""

    output_dir = Path("/tmp/makemoney_frames")
    output_dir.mkdir(exist_ok=True)

    video_file = Path(__file__).parent / "hero-bots.mp4"
    fps = 30
    duration_seconds = 10
    total_frames = fps * duration_seconds

    print(f"Generating {total_frames} frames...")

    for i in range(total_frames):
        if i % 30 == 0:
            print(f"  Frame {i}/{total_frames}")

        frame = create_frame(i, total_frames, fps)
        frame.save(f"{output_dir}/frame_{i:04d}.png")

    print(f"Encoding video to {video_file}...")

    cmd = [
        "ffmpeg",
        "-framerate", str(fps),
        "-i", str(output_dir / "frame_%04d.png"),
        "-c:v", "libx264",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-y",
        str(video_file)
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ Video created: {video_file}")
        size_mb = video_file.stat().st_size / 1024 / 1024
        print(f"   Size: {size_mb:.1f} MB")

        # Cleanup frames
        import shutil
        shutil.rmtree(output_dir)

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    generate_video()
