#!/usr/bin/env python3
"""
Hero video: Focus on animated BOTS, not code.
Bots + glows + data flow + revenue (minimal text).
"""

import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

def create_frame(frame_num, total_frames, fps=30):
    """Frame focused on bot animations."""

    width, height = 1920, 1080
    img = Image.new('RGB', (width, height), color='#0a1628')
    draw = ImageDraw.Draw(img, 'RGBA')

    t = frame_num / fps

    try:
        big_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 72)
    except:
        big_font = ImageFont.load_default()

    # Background: subtle grid
    for x in range(0, width, 120):
        draw.line([(x, 0), (x, height)], fill=(0, 217, 255, 5), width=1)
    for y in range(0, height, 120):
        draw.line([(0, y), (width, y)], fill=(0, 217, 255, 5), width=1)

    # === MAIN: THREE BOTS (FORMING TRIANGLE) ===

    # Bot 1 (LEFT) - Cyan
    bot1_x = width // 4
    bot1_y = 350
    pulse1 = 140 + 100 * math.sin(2 * math.pi * t / 2.8)

    # Bots with multiple glow layers
    for ring in range(5, 0, -1):
        glow_alpha = int(80 / (ring + 1))
        glow_size = pulse1 + ring * 35
        draw.ellipse(
            [(bot1_x - glow_size//2, bot1_y - glow_size//2),
             (bot1_x + glow_size//2, bot1_y + glow_size//2)],
            outline=(0, 217, 255, glow_alpha),
            width=1
        )

    # Core bot
    draw.ellipse(
        [(bot1_x - 80, bot1_y - 80),
         (bot1_x + 80, bot1_y + 80)],
        fill=(0, 217, 255, 240),
        outline=(0, 255, 255, 255),
        width=4
    )

    # Eyes
    eye_dist = 30
    draw.ellipse([(bot1_x - eye_dist - 15, bot1_y - 15), (bot1_x - eye_dist + 15, bot1_y + 15)],
                 fill=(5, 16, 32))
    draw.ellipse([(bot1_x + eye_dist - 15, bot1_y - 15), (bot1_x + eye_dist + 15, bot1_y + 15)],
                 fill=(5, 16, 32))

    # Bot 2 (RIGHT) - Green
    bot2_x = 3 * width // 4
    bot2_y = 350
    pulse2 = 140 + 100 * math.cos(2 * math.pi * t / 2.8)

    for ring in range(5, 0, -1):
        glow_alpha = int(80 / (ring + 1))
        glow_size = pulse2 + ring * 35
        draw.ellipse(
            [(bot2_x - glow_size//2, bot2_y - glow_size//2),
             (bot2_x + glow_size//2, bot2_y + glow_size//2)],
            outline=(16, 185, 129, glow_alpha),
            width=1
        )

    # Core bot
    draw.ellipse(
        [(bot2_x - 80, bot2_y - 80),
         (bot2_x + 80, bot2_y + 80)],
        fill=(16, 185, 129, 240),
        outline=(0, 255, 100, 255),
        width=4
    )

    # Eyes
    draw.ellipse([(bot2_x - eye_dist - 15, bot2_y - 15), (bot2_x - eye_dist + 15, bot2_y + 15)],
                 fill=(5, 16, 32))
    draw.ellipse([(bot2_x + eye_dist - 15, bot2_y - 15), (bot2_x + eye_dist + 15, bot2_y + 15)],
                 fill=(5, 16, 32))

    # Bot 3 (TOP CENTER) - Gold/Yellow
    bot3_x = width // 2
    bot3_y = 150
    pulse3 = 140 + 100 * math.sin(2 * math.pi * (t + 0.5) / 2.8)

    for ring in range(5, 0, -1):
        glow_alpha = int(80 / (ring + 1))
        glow_size = pulse3 + ring * 35
        draw.ellipse(
            [(bot3_x - glow_size//2, bot3_y - glow_size//2),
             (bot3_x + glow_size//2, bot3_y + glow_size//2)],
            outline=(255, 215, 0, glow_alpha),
            width=1
        )

    # Core bot
    draw.ellipse(
        [(bot3_x - 80, bot3_y - 80),
         (bot3_x + 80, bot3_y + 80)],
        fill=(255, 215, 0, 240),
        outline=(255, 255, 100, 255),
        width=4
    )

    # Eyes
    draw.ellipse([(bot3_x - eye_dist - 15, bot3_y - 15), (bot3_x - eye_dist + 15, bot3_y + 15)],
                 fill=(5, 16, 32))
    draw.ellipse([(bot3_x + eye_dist - 15, bot3_y - 15), (bot3_x + eye_dist + 15, bot3_y + 15)],
                 fill=(5, 16, 32))

    # === DATA FLOW: CONNECTIONS BETWEEN BOTS ===

    # Bot1 <-> Bot2 (bottom line)
    flow_1_2 = (t * 0.5) % 1  # Slower flow
    flow_x_1_2 = bot1_x + (bot2_x - bot1_x) * flow_1_2
    flow_y_1_2 = bot1_y + (bot1_y - bot1_y) * flow_1_2  # Same Y

    draw.line([(bot1_x, bot1_y), (bot2_x, bot2_y)],
              fill=(0, 217, 255, 100), width=3)

    # Packets on line 1-2
    for offset in range(0, 100, 25):
        px = bot1_x + (bot2_x - bot1_x) * ((flow_1_2 + offset / 100) % 1)
        py = bot1_y
        draw.ellipse([(px - 15, py - 15), (px + 15, py + 15)],
                    fill=(255, 215, 0, 220))
        draw.ellipse([(px - 25, py - 25), (px + 25, py + 25)],
                    outline=(255, 215, 0, 120), width=2)

    # Bot1 -> Bot3 (diagonal)
    draw.line([(bot1_x, bot1_y), (bot3_x, bot3_y)],
              fill=(16, 185, 129, 100), width=3)

    flow_1_3 = (t * 0.5 + 0.33) % 1
    for offset in range(0, 100, 25):
        progress = (flow_1_3 + offset / 100) % 1
        px = bot1_x + (bot3_x - bot1_x) * progress
        py = bot1_y + (bot3_y - bot1_y) * progress
        draw.ellipse([(px - 15, py - 15), (px + 15, py + 15)],
                    fill=(255, 215, 0, 220))

    # Bot2 -> Bot3 (diagonal)
    draw.line([(bot2_x, bot2_y), (bot3_x, bot3_y)],
              fill=(0, 217, 255, 100), width=3)

    flow_2_3 = (t * 0.5 + 0.67) % 1
    for offset in range(0, 100, 25):
        progress = (flow_2_3 + offset / 100) % 1
        px = bot2_x + (bot3_x - bot2_x) * progress
        py = bot2_y + (bot3_y - bot2_y) * progress
        draw.ellipse([(px - 15, py - 15), (px + 15, py + 15)],
                    fill=(255, 215, 0, 220))

    # === SIMPLE TEXT: Just revenue ===
    if t > 3:
        counter_alpha = min(255, int(255 * (t - 3) / 1.5))
        revenue = min(100000, int(100000 * (t - 3) / 8))
        revenue_text = f"${revenue:,}"

        if counter_alpha > 0:
            # Glow
            for offset in range(1, 6):
                draw.text(
                    (width//2 - 250 + offset, 700 + offset),
                    revenue_text,
                    font=big_font,
                    fill=(16, 185, 129, counter_alpha // 4)
                )
            # Main
            draw.text(
                (width//2 - 250, 700),
                revenue_text,
                font=big_font,
                fill=(16, 185, 129, counter_alpha)
            )

    # === STATUS: All bots "active" ===
    for bot_x, bot_y, color in [(bot1_x, bot1_y, (0, 217, 255)),
                                 (bot2_x, bot2_y, (16, 185, 129)),
                                 (bot3_x, bot3_y, (255, 215, 0))]:
        status_alpha = int(200 * (0.5 + 0.5 * math.sin(2 * math.pi * t * 2)))
        draw.ellipse(
            [(bot_x - 120, bot_y + 110), (bot_x - 90, bot_y + 140)],
            fill=(*color, status_alpha)
        )

    return img

def generate_video():
    """Generate MP4."""

    output_dir = Path("/tmp/makemoney_frames_bots")
    output_dir.mkdir(exist_ok=True)

    video_file = Path(__file__).parent / "hero-bots.mp4"
    fps = 30
    duration_seconds = 14
    total_frames = fps * duration_seconds

    print(f"Generating {total_frames} frames (bots focus)...")

    for i in range(total_frames):
        if i % 30 == 0:
            print(f"  Frame {i}/{total_frames}")

        frame = create_frame(i, total_frames, fps)
        frame.save(f"{output_dir}/frame_{i:04d}.png")

    print(f"Encoding...")

    cmd = [
        "ffmpeg",
        "-framerate", str(fps),
        "-i", str(output_dir / "frame_%04d.png"),
        "-c:v", "libx264",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-y",
        str(video_file)
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        size_mb = video_file.stat().st_size / 1024 / 1024
        print(f"Done: {size_mb:.1f} MB")

        import shutil
        shutil.rmtree(output_dir)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    generate_video()
