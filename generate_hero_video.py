#!/usr/bin/env python3
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

def create_frame(frame_num, total_frames, fps=30):
    width, height = 1920, 1080
    img = Image.new('RGB', (width, height), color='#0a1a2e')
    draw = ImageDraw.Draw(img, 'RGBA')

    t = frame_num / fps

    try:
        big_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 140)
        medium_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 72)
        small_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 48)
    except:
        big_font = ImageFont.load_default()
        medium_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Futuristic background: scanning lines effect
    for y in range(0, height, 8):
        line_alpha = int(20 * (0.3 + 0.7 * math.sin(2 * math.pi * (t + y/height) / 2)))
        draw.line([(0, y), (width, y)], fill=(0, 217, 255, line_alpha), width=1)

    # Holographic grid (perspective)
    grid_alpha = int(30 * (0.5 + 0.5 * math.sin(2 * math.pi * t / 3)))
    for x in range(0, width, 150):
        # Vertical lines
        start_y = height // 2 - (width // 2 - x) * 0.3
        end_y = height - (width // 2 - x) * 0.3
        draw.line([(x, int(start_y)), (x, int(end_y))],
                 fill=(0, 217, 255, grid_alpha), width=1)

    for y in range(0, height, 150):
        # Horizontal lines
        start_x = width // 2 - (height // 2 - y) * 0.3
        end_x = width - (height // 2 - y) * 0.3
        draw.line([(int(start_x), y), (int(end_x), y)],
                 fill=(0, 217, 255, grid_alpha), width=1)

    # === CENTRAL HOLOGRAPHIC DISPLAY (DIAMOND SHAPE) ===
    center_x, center_y = width // 2, height // 2

    # Rotating diamond frame
    rotation = 2 * math.pi * t / 5
    diamond_size = 300

    corners = [
        (center_x + diamond_size * math.cos(rotation),
         center_y + diamond_size * math.sin(rotation)),
        (center_x + diamond_size * math.cos(rotation + math.pi/2),
         center_y + diamond_size * math.sin(rotation + math.pi/2)),
        (center_x + diamond_size * math.cos(rotation + math.pi),
         center_y + diamond_size * math.sin(rotation + math.pi)),
        (center_x + diamond_size * math.cos(rotation + 3*math.pi/2),
         center_y + diamond_size * math.sin(rotation + 3*math.pi/2)),
    ]

    # Draw diamond outline
    for i in range(4):
        p1 = corners[i]
        p2 = corners[(i + 1) % 4]
        draw.line([p1, p2], fill=(0, 217, 255, 200), width=3)

    # Diamond glow
    glow_radius = diamond_size * 1.3
    for ring in range(5, 0, -1):
        ring_alpha = int(50 / (ring + 1))
        ring_size = glow_radius + ring * 30
        draw.ellipse(
            [(center_x - ring_size, center_y - ring_size),
             (center_x + ring_size, center_y + ring_size)],
            outline=(0, 217, 255, ring_alpha),
            width=1
        )

    # === ANIMATED DATA STREAMS (INSIDE DIAMOND) ===
    for stream_num in range(3):
        stream_start = t * 400 + stream_num * 120

        # Vertical data streams
        for pos in range(0, int(stream_start) % 800, 80):
            y_pos = center_y - 250 + pos
            alpha = max(0, 255 - abs(pos - (int(stream_start) % 800)) // 2)
            draw.ellipse(
                [(center_x - 80 + stream_num * 80 - 10, y_pos - 10),
                 (center_x - 80 + stream_num * 80 + 10, y_pos + 10)],
                fill=(16, 185, 129, int(alpha))
            )

    # === PROCESSING INDICATORS (AROUND DIAMOND) ===
    for i in range(6):
        angle = 2 * math.pi * (t / 3 + i / 6)
        ind_x = center_x + (diamond_size + 200) * math.cos(angle)
        ind_y = center_y + (diamond_size + 200) * math.sin(angle)

        # Indicator glow
        glow_alpha = int(150 * (0.5 + 0.5 * math.sin(2 * math.pi * (t + i) / 2)))
        draw.ellipse(
            [(ind_x - 35, ind_y - 35), (ind_x + 35, ind_y + 35)],
            outline=(255, 215, 0, glow_alpha),
            width=2
        )

        # Indicator core
        draw.ellipse(
            [(ind_x - 20, ind_y - 20), (ind_x + 20, ind_y + 20)],
            fill=(255, 215, 0, 200)
        )

    # === LARGE REVENUE DISPLAY (CENTER) ===
    if t > 1:
        revenue_alpha = min(255, int(255 * (t - 1) / 1.5))
        revenue = min(99999999, int(99999999 * (t - 1) / 12))

        revenue_text = f"${revenue:,}"

        # Glow effect
        for offset in range(2, 8):
            draw.text((center_x - 280 + offset, center_y - 50 + offset),
                     revenue_text,
                     font=big_font,
                     fill=(16, 185, 129, revenue_alpha // 5))

        # Main text
        draw.text((center_x - 280, center_y - 50),
                 revenue_text,
                 font=big_font,
                 fill=(16, 185, 129, revenue_alpha))

    # === TOP TEXT ===
    if t > 0.3:
        text_alpha = min(255, int(255 * (t - 0.3) / 1))

        # "AI POWERED"
        for offset in range(1, 4):
            draw.text((150 + offset, 100 + offset), "AI POWERED",
                     font=medium_font, fill=(0, 217, 255, text_alpha // 3))
        draw.text((150, 100), "AI POWERED",
                 font=medium_font, fill=(0, 217, 255, text_alpha))

    # === BOTTOM TEXT ===
    if t > 0.5:
        text_alpha = min(255, int(255 * (t - 0.5) / 1))

        # "AUTONOMOUS REVENUE"
        bottom_text = "AUTONOMOUS REVENUE"
        for offset in range(1, 4):
            draw.text((width - 800 + offset, height - 150 + offset), bottom_text,
                     font=medium_font, fill=(255, 215, 0, text_alpha // 3))
        draw.text((width - 800, height - 150), bottom_text,
                 font=medium_font, fill=(255, 215, 0, text_alpha))

    # === CORNER TECH ELEMENTS ===
    corners_data = [
        (80, 80, (0, 217, 255)),
        (width - 80, 80, (0, 217, 255)),
        (80, height - 80, (16, 185, 129)),
        (width - 80, height - 80, (255, 215, 0)),
    ]

    for corner_x, corner_y, color in corners_data:
        corner_alpha = int(150 * (0.5 + 0.5 * math.sin(2 * math.pi * t * 2)))
        # Bracket effect
        draw.line([(corner_x - 40, corner_y - 40), (corner_x - 40, corner_y + 40)],
                 fill=(*color, corner_alpha), width=2)
        draw.line([(corner_x - 40, corner_y - 40), (corner_x + 40, corner_y - 40)],
                 fill=(*color, corner_alpha), width=2)
        draw.ellipse([(corner_x - 15, corner_y - 15), (corner_x + 15, corner_y + 15)],
                    fill=(*color, corner_alpha // 2))

    return img

def generate_video():
    output_dir = Path("/tmp/makemoney_ai_tech")
    output_dir.mkdir(exist_ok=True)

    video_file = Path(__file__).parent / "hero-bots.mp4"
    fps = 30
    duration_seconds = 16
    total_frames = fps * duration_seconds

    print(f"Creating futuristic AI tech video...")

    for i in range(total_frames):
        if i % 60 == 0:
            print(f"  {i}/{total_frames}")
        frame = create_frame(i, total_frames, fps)
        frame.save(f"{output_dir}/frame_{i:04d}.png")

    print("Encoding...")
    cmd = [
        "ffmpeg", "-framerate", str(fps),
        "-i", str(output_dir / "frame_%04d.png"),
        "-c:v", "libx264", "-crf", "15", "-pix_fmt", "yuv420p",
        "-y", str(video_file)
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        size_mb = video_file.stat().st_size / 1024 / 1024
        print(f"Video ready: {size_mb:.1f} MB")
        import shutil
        shutil.rmtree(output_dir)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    generate_video()
