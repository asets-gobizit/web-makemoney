#!/usr/bin/env python3
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

def create_frame(frame_num, total_frames, fps=30):
    width, height = 1920, 1080
    img = Image.new('RGB', (width, height), color='#0a1628')
    draw = ImageDraw.Draw(img, 'RGBA')

    t = frame_num / fps

    try:
        big_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 96)
        medium_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 48)
    except:
        big_font = ImageFont.load_default()
        medium_font = ImageFont.load_default()

    # Animated grid background
    for x in range(0, width, 150):
        alpha = int(20 * (0.3 + 0.7 * math.sin(2 * math.pi * (t + x/width) / 3)))
        draw.line([(x, 0), (x, height)], fill=(0, 217, 255, alpha), width=1)
    for y in range(0, height, 150):
        alpha = int(20 * (0.3 + 0.7 * math.sin(2 * math.pi * (t + y/height) / 3)))
        draw.line([(0, y), (width, y)], fill=(0, 217, 255, alpha), width=1)

    # Central bot (large, dominant)
    center_x, center_y = width // 2, height // 2
    main_pulse = 180 + 120 * math.sin(2 * math.pi * t / 3)

    # Outer rings
    for ring in range(8, 0, -1):
        ring_alpha = int(100 * (1 - ring / 10))
        ring_size = main_pulse + ring * 40
        draw.ellipse(
            [(center_x - ring_size//2, center_y - ring_size//2),
             (center_x + ring_size//2, center_y + ring_size//2)],
            outline=(0, 217, 255, ring_alpha),
            width=2
        )

    # Main bot core (very bright)
    draw.ellipse(
        [(center_x - 100, center_y - 100),
         (center_x + 100, center_y + 100)],
        fill=(0, 217, 255, 255),
        outline=(0, 255, 255, 255),
        width=5
    )

    # Bot face
    eye_y = center_y - 20
    draw.ellipse([(center_x - 35, eye_y - 20), (center_x - 15, eye_y + 20)],
                 fill=(5, 16, 32, 255))
    draw.ellipse([(center_x + 15, eye_y - 20), (center_x + 35, eye_y + 20)],
                 fill=(5, 16, 32, 255))

    # Mouth indicator (pulsing)
    mouth_alpha = int(150 * (0.5 + 0.5 * math.sin(2 * math.pi * t)))
    draw.line([(center_x - 30, center_y + 40), (center_x + 30, center_y + 40)],
              fill=(0, 255, 255, mouth_alpha), width=4)

    # Orbiting smaller bots (3 satellites)
    for i in range(3):
        angle = 2 * math.pi * (t / 4 + i / 3)
        orbit_x = center_x + 400 * math.cos(angle)
        orbit_y = center_y + 300 * math.sin(angle)

        colors = [(16, 185, 129), (255, 215, 0), (100, 200, 255)]
        color = colors[i]

        # Satellite glow
        for ring in range(3, 0, -1):
            ring_alpha = int(80 / (ring + 1))
            ring_size = 80 + ring * 20
            draw.ellipse(
                [(orbit_x - ring_size//2, orbit_y - ring_size//2),
                 (orbit_x + ring_size//2, orbit_y + ring_size//2)],
                outline=(*color, ring_alpha),
                width=1
            )

        # Satellite core
        draw.ellipse(
            [(orbit_x - 50, orbit_y - 50),
             (orbit_x + 50, orbit_y + 50)],
            fill=(*color, 220),
            outline=(*color, 255),
            width=3
        )

        # Connection line to main bot
        line_alpha = int(150 * (0.5 + 0.5 * math.sin(2 * math.pi * t * 2)))
        draw.line(
            [(center_x, center_y), (orbit_x, orbit_y)],
            fill=(*color, line_alpha),
            width=2
        )

        # Data packets on connection
        for packet_num in range(3):
            packet_progress = (t * 0.8 + packet_num / 3) % 1
            packet_x = center_x + (orbit_x - center_x) * packet_progress
            packet_y = center_y + (orbit_y - center_y) * packet_progress

            draw.ellipse(
                [(packet_x - 12, packet_y - 12),
                 (packet_x + 12, packet_y + 12)],
                fill=(255, 215, 0, 200)
            )

    # Revenue display (lower right)
    if t > 2:
        revenue_alpha = min(255, int(255 * (t - 2) / 2))
        revenue = min(999999, int(999999 * (t - 2) / 10))

        # Animated dollar sign
        draw.text((width - 450, height - 200), "$",
                 font=big_font, fill=(16, 185, 129, revenue_alpha))

        # Revenue number
        revenue_text = f"{revenue:,}"
        draw.text((width - 380, height - 200), revenue_text,
                 font=medium_font, fill=(16, 185, 129, revenue_alpha))

    # Status text (upper left)
    if t > 1:
        status_alpha = min(255, int(255 * (t - 1) / 1))
        draw.text((60, 80), "AUTONOMOUS",
                 font=medium_font, fill=(0, 217, 255, status_alpha))
        draw.text((60, 150), "AGENT ACTIVE",
                 font=medium_font, fill=(0, 217, 255, status_alpha))

    return img

def generate_video():
    output_dir = Path("/tmp/makemoney_final")
    output_dir.mkdir(exist_ok=True)

    video_file = Path(__file__).parent / "hero-bots.mp4"
    fps = 30
    duration_seconds = 12
    total_frames = fps * duration_seconds

    print(f"Creating final hero video ({total_frames} frames)...")

    for i in range(total_frames):
        if i % 60 == 0:
            print(f"  {i}/{total_frames}")
        frame = create_frame(i, total_frames, fps)
        frame.save(f"{output_dir}/frame_{i:04d}.png")

    print("Encoding...")
    cmd = [
        "ffmpeg", "-framerate", str(fps),
        "-i", str(output_dir / "frame_%04d.png"),
        "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
        "-y", str(video_file)
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        size_mb = video_file.stat().st_size / 1024 / 1024
        print(f"Video complete: {size_mb:.1f} MB")
        import shutil
        shutil.rmtree(output_dir)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    generate_video()
