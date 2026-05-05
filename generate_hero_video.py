#!/usr/bin/env python3
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

def create_frame(frame_num, total_frames, fps=30):
    width, height = 1920, 1080
    img = Image.new('RGB', (width, height), color='#051020')
    draw = ImageDraw.Draw(img, 'RGBA')

    t = frame_num / fps

    try:
        big_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 120)
        medium_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 56)
    except:
        big_font = ImageFont.load_default()
        medium_font = ImageFont.load_default()

    # Dynamic background with flowing waves
    for y in range(0, height, 60):
        wave_offset = 80 * math.sin(2 * math.pi * (t / 4 + y / height))
        draw.line([(0, y + wave_offset), (width, y + wave_offset)],
                 fill=(0, 217, 255, int(15 * (1 - y/height))), width=2)

    # Three main bots in triangle (VERY LARGE AND PROMINENT)
    bot1_x, bot1_y = 300, 600  # Left
    bot2_x, bot2_y = width - 300, 600  # Right
    bot3_x, bot3_y = width // 2, 200  # Top

    # === BOT 1 (LEFT - CYAN) ===
    pulse1 = 200 + 150 * math.sin(2 * math.pi * t / 2.5)
    for ring in range(10, 0, -1):
        ring_alpha = int(120 * (1 - ring / 12))
        ring_size = pulse1 + ring * 35
        draw.ellipse(
            [(bot1_x - ring_size//2, bot1_y - ring_size//2),
             (bot1_x + ring_size//2, bot1_y + ring_size//2)],
            outline=(0, 217, 255, ring_alpha),
            width=3
        )

    draw.ellipse([(bot1_x - 120, bot1_y - 120), (bot1_x + 120, bot1_y + 120)],
                 fill=(0, 217, 255, 255),
                 outline=(100, 255, 255, 255), width=6)
    draw.ellipse([(bot1_x - 35, bot1_y - 35), (bot1_x + 35, bot1_y + 35)],
                 fill=(5, 16, 32, 255))

    # === BOT 2 (RIGHT - GREEN) ===
    pulse2 = 200 + 150 * math.cos(2 * math.pi * t / 2.5)
    for ring in range(10, 0, -1):
        ring_alpha = int(120 * (1 - ring / 12))
        ring_size = pulse2 + ring * 35
        draw.ellipse(
            [(bot2_x - ring_size//2, bot2_y - ring_size//2),
             (bot2_x + ring_size//2, bot2_y + ring_size//2)],
            outline=(16, 185, 129, ring_alpha),
            width=3
        )

    draw.ellipse([(bot2_x - 120, bot2_y - 120), (bot2_x + 120, bot2_y + 120)],
                 fill=(16, 185, 129, 255),
                 outline=(100, 255, 150, 255), width=6)
    draw.ellipse([(bot2_x - 35, bot2_y - 35), (bot2_x + 35, bot2_y + 35)],
                 fill=(5, 16, 32, 255))

    # === BOT 3 (TOP - GOLD) ===
    pulse3 = 200 + 150 * math.sin(2 * math.pi * (t + 1.25) / 2.5)
    for ring in range(10, 0, -1):
        ring_alpha = int(120 * (1 - ring / 12))
        ring_size = pulse3 + ring * 35
        draw.ellipse(
            [(bot3_x - ring_size//2, bot3_y - ring_size//2),
             (bot3_x + ring_size//2, bot3_y + ring_size//2)],
            outline=(255, 215, 0, ring_alpha),
            width=3
        )

    draw.ellipse([(bot3_x - 120, bot3_y - 120), (bot3_x + 120, bot3_y + 120)],
                 fill=(255, 215, 0, 255),
                 outline=(255, 255, 150, 255), width=6)
    draw.ellipse([(bot3_x - 35, bot3_y - 35), (bot3_x + 35, bot3_y + 35)],
                 fill=(5, 16, 32, 255))

    # === MEGA DATA FLOWS (THICK, BRIGHT, ANIMATED) ===
    line_width = 4 + int(2 * math.sin(2 * math.pi * t * 3))

    # Flow 1->2 (bottom)
    draw.line([(bot1_x, bot1_y), (bot2_x, bot2_y)],
              fill=(0, 217, 255, 200), width=line_width)

    # Flow 1->3 (diagonal)
    draw.line([(bot1_x, bot1_y), (bot3_x, bot3_y)],
              fill=(16, 185, 129, 200), width=line_width)

    # Flow 2->3 (diagonal)
    draw.line([(bot2_x, bot2_y), (bot3_x, bot3_y)],
              fill=(255, 215, 0, 200), width=line_width)

    # MASSIVE MOVING PACKETS
    for connection_num, (x1, y1, x2, y2, color) in enumerate([
        (bot1_x, bot1_y, bot2_x, bot2_y, (0, 217, 255)),
        (bot1_x, bot1_y, bot3_x, bot3_y, (16, 185, 129)),
        (bot2_x, bot2_y, bot3_x, bot3_y, (255, 215, 0)),
    ]):
        for packet_num in range(4):
            progress = (t * 1.2 + packet_num * 0.25 + connection_num * 0.33) % 1
            px = x1 + (x2 - x1) * progress
            py = y1 + (y2 - y1) * progress

            # Packet glow
            draw.ellipse([(px - 35, py - 35), (px + 35, py + 35)],
                        outline=(*color, 180), width=3)
            # Packet core (BRIGHT)
            draw.ellipse([(px - 25, py - 25), (px + 25, py + 25)],
                        fill=(*color, 255))

    # === LARGE REVENUE COUNTER (BOTTOM CENTER) ===
    if t > 1.5:
        revenue_alpha = min(255, int(255 * (t - 1.5) / 1.5))
        revenue = min(9999999, int(9999999 * (t - 1.5) / 10))

        revenue_text = f"${revenue:,}"
        text_bbox = draw.textbbox((0, 0), revenue_text, font=big_font)
        text_width = text_bbox[2] - text_bbox[0]

        draw.text((width // 2 - text_width // 2, height - 180),
                 revenue_text,
                 font=big_font,
                 fill=(16, 185, 129, revenue_alpha))

    # === STATUS INDICATORS ===
    status_glow = int(200 * (0.6 + 0.4 * math.sin(2 * math.pi * t * 2)))

    # Status dots below each bot
    for bot_x, bot_y, color in [(bot1_x, bot1_y, (0, 217, 255)),
                                (bot2_x, bot2_y, (16, 185, 129)),
                                (bot3_x, bot3_y, (255, 215, 0))]:
        draw.ellipse([(bot_x - 40, bot_y + 160), (bot_x + 40, bot_y + 240)],
                    fill=(*color, status_glow // 2))
        draw.ellipse([(bot_x - 30, bot_y + 170), (bot_x + 30, bot_y + 230)],
                    outline=(*color, 255), width=3)

    return img

def generate_video():
    output_dir = Path("/tmp/makemoney_hero_v4")
    output_dir.mkdir(exist_ok=True)

    video_file = Path(__file__).parent / "hero-bots.mp4"
    fps = 30
    duration_seconds = 14
    total_frames = fps * duration_seconds

    print(f"Creating premium hero video...")

    for i in range(total_frames):
        if i % 60 == 0:
            print(f"  {i}/{total_frames}")
        frame = create_frame(i, total_frames, fps)
        frame.save(f"{output_dir}/frame_{i:04d}.png")

    print("Encoding to MP4...")
    cmd = [
        "ffmpeg", "-framerate", str(fps),
        "-i", str(output_dir / "frame_%04d.png"),
        "-c:v", "libx264", "-crf", "15", "-pix_fmt", "yuv420p",
        "-y", str(video_file)
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        size_mb = video_file.stat().st_size / 1024 / 1024
        print(f"Premium video ready: {size_mb:.1f} MB")
        import shutil
        shutil.rmtree(output_dir)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    generate_video()
