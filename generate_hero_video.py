#!/usr/bin/env python3
"""
Generate improved hero video with VISIBLE bots + code + glowing effects.
"""

import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

def create_frame(frame_num, total_frames, fps=30):
    """Create frame with bright, visible animations."""

    width, height = 1920, 1080

    # Dark background with subtle gradient
    img = Image.new('RGB', (width, height), color='#0a1628')
    draw = ImageDraw.Draw(img, 'RGBA')

    t = frame_num / fps

    # Load fonts
    try:
        code_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 52)
        big_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 88)
    except:
        code_font = ImageFont.load_default()
        big_font = ImageFont.load_default()

    # Background: subtle grid effect
    for x in range(0, width, 100):
        draw.line([(x, 0), (x, height)], fill=(0, 217, 255, 8), width=1)
    for y in range(0, height, 100):
        draw.line([(0, y), (width, y)], fill=(0, 217, 255, 8), width=1)

    # === CODE LINES (LEFT SIDE) ===
    code_lines = [
        ("const agent = new AIBot();", 150, (0, 217, 255), 0.2, 2.5),  # Cyan
        ("await agent.execute(task);", 250, (16, 185, 129), 1.2, 3.5),  # Green
        ("revenue = agent.earnings();", 350, (255, 215, 0), 2.2, 4.5),  # Gold
    ]

    for text, y_pos, color, fade_in, fade_out in code_lines:
        alpha = 255

        # Fade in
        if t < fade_in:
            alpha = int(255 * (t / fade_in))
        # Fade out
        elif t > fade_out:
            alpha = int(255 * max(0, (5 - t) / 0.5))

        if alpha > 10:
            # Bright glow layer
            for offset in range(2, 8):
                draw.text((100 + offset, y_pos + offset), text,
                         font=code_font, fill=(*color, alpha // 8))

            # Main text (bright)
            draw.text((100, y_pos), text,
                     font=code_font, fill=(*color, alpha))

    # === BOT NODES (RIGHT SIDE) ===
    bot_y = 200

    # LEFT BOT (Cyan) - pulsing
    bot_left_x = width // 4
    pulse_size = 120 + 80 * math.sin(2 * math.pi * t / 2.5)

    # Outer glow (multiple rings)
    for ring in range(3, 0, -1):
        glow_alpha = int(100 / (ring + 1))
        glow_size = pulse_size + ring * 30
        draw.ellipse(
            [(bot_left_x - glow_size//2, bot_y - glow_size//2),
             (bot_left_x + glow_size//2, bot_y + glow_size//2)],
            outline=(0, 217, 255, glow_alpha),
            width=2
        )

    # Core bot
    draw.ellipse(
        [(bot_left_x - 60, bot_y - 60),
         (bot_left_x + 60, bot_y + 60)],
        fill=(0, 217, 255, 220),
        outline=(0, 255, 255, 255),
        width=3
    )

    # Eye indicator
    draw.ellipse(
        [(bot_left_x - 15, bot_y - 15),
         (bot_left_x + 15, bot_y + 15)],
        fill=(5, 16, 32, 200)
    )

    # RIGHT BOT (Green) - pulsing opposite
    bot_right_x = 3 * width // 4
    pulse_size2 = 120 + 80 * math.cos(2 * math.pi * t / 2.5)

    # Outer glow
    for ring in range(3, 0, -1):
        glow_alpha = int(100 / (ring + 1))
        glow_size = pulse_size2 + ring * 30
        draw.ellipse(
            [(bot_right_x - glow_size//2, bot_y - glow_size//2),
             (bot_right_x + glow_size//2, bot_y + glow_size//2)],
            outline=(16, 185, 129, glow_alpha),
            width=2
        )

    # Core bot
    draw.ellipse(
        [(bot_right_x - 60, bot_y - 60),
         (bot_right_x + 60, bot_y + 60)],
        fill=(16, 185, 129, 220),
        outline=(0, 255, 100, 255),
        width=3
    )

    # Eye indicator
    draw.ellipse(
        [(bot_right_x - 15, bot_y - 15),
         (bot_right_x + 15, bot_y + 15)],
        fill=(5, 16, 32, 200)
    )

    # === DATA FLOW BETWEEN BOTS ===
    flow_progress = (t % 2) / 2  # 0 to 1, loops every 2 seconds
    flow_x = bot_left_x + (bot_right_x - bot_left_x) * flow_progress

    # Connecting line (pulsing width)
    line_width = 2 + int(3 * math.sin(2 * math.pi * t))
    draw.line(
        [(bot_left_x, bot_y), (bot_right_x, bot_y)],
        fill=(0, 217, 255, 120),
        width=line_width
    )

    # Data packets moving along line (bright dots)
    for packet_offset in range(0, 200, 50):
        packet_x = bot_left_x + (bot_right_x - bot_left_x) * ((flow_progress + packet_offset / 200) % 1)
        draw.ellipse(
            [(packet_x - 12, bot_y - 12),
             (packet_x + 12, bot_y + 12)],
            fill=(255, 215, 0, 200)
        )
        # Glow around packet
        draw.ellipse(
            [(packet_x - 20, bot_y - 20),
             (packet_x + 20, bot_y + 20)],
            outline=(255, 215, 0, 100),
            width=2
        )

    # === REVENUE COUNTER (CENTER BOTTOM) ===
    if t > 2.5:
        counter_alpha = min(255, int(255 * (t - 2.5) / 1.5))
        revenue = min(50000, int(50000 * (t - 2.5) / 5))
        revenue_text = f"${revenue:,}"

        if counter_alpha > 0:
            # Glow
            for offset in range(1, 6):
                draw.text(
                    (width//2 - 200 + offset, 550 + offset),
                    revenue_text,
                    font=big_font,
                    fill=(16, 185, 129, counter_alpha // 4)
                )

            # Main text
            draw.text(
                (width//2 - 200, 550),
                revenue_text,
                font=big_font,
                fill=(16, 185, 129, counter_alpha)
            )

    # === STATUS INDICATOR (TOP RIGHT) ===
    status_alpha = int(255 * (0.5 + 0.5 * math.sin(2 * math.pi * t)))
    draw.ellipse(
        [(width - 120, 80), (width - 80, 120)],
        fill=(16, 185, 129, status_alpha)
    )
    # Glow
    draw.ellipse(
        [(width - 130, 70), (width - 70, 130)],
        outline=(16, 185, 129, status_alpha // 2),
        width=2
    )

    return img

def generate_video():
    """Create MP4 from frames."""

    output_dir = Path("/tmp/makemoney_frames_v2")
    output_dir.mkdir(exist_ok=True)

    video_file = Path(__file__).parent / "hero-bots.mp4"
    fps = 30
    duration_seconds = 12
    total_frames = fps * duration_seconds

    print(f"Generating {total_frames} frames (improved visibility)...")

    for i in range(total_frames):
        if i % 30 == 0:
            print(f"  Frame {i}/{total_frames}")

        frame = create_frame(i, total_frames, fps)
        frame.save(f"{output_dir}/frame_{i:04d}.png")

    print(f"Encoding video...")

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
        print(f"Video created: {size_mb:.1f} MB")

        # Cleanup
        import shutil
        shutil.rmtree(output_dir)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    generate_video()
