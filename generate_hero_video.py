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
        big_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 180)
        medium_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 80)
        small_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 56)
    except:
        big_font = ImageFont.load_default()
        medium_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Background gradient
    for y in range(0, height, 20):
        alpha = int(10 + 10 * (y / height))
        draw.rectangle([(0, y), (width, y + 20)], fill=(0, 50, 100, alpha))

    # === LEFT SIDE: NEURAL NETWORK (AI) ===
    ai_start_x = 150
    ai_start_y = height // 2

    # Neural network nodes (5 clusters)
    node_positions = []
    for layer in range(3):
        layer_x = ai_start_x + layer * 180
        for node in range(4):
            node_y = 200 + node * 200
            node_positions.append((layer_x, node_y))

            # Node glow
            glow_alpha = int(100 * (0.5 + 0.5 * math.sin(2 * math.pi * (t + layer + node) / 3)))
            draw.ellipse(
                [(layer_x - 40, node_y - 40), (layer_x + 40, node_y + 40)],
                outline=(0, 217, 255, glow_alpha),
                width=2
            )

            # Node core
            draw.ellipse(
                [(layer_x - 25, node_y - 25), (layer_x + 25, node_y + 25)],
                fill=(0, 217, 255, 200)
            )

    # Connections between nodes (synapses)
    for i in range(len(node_positions) - 1):
        x1, y1 = node_positions[i]
        x2, y2 = node_positions[i + 1] if i + 1 < len(node_positions) else node_positions[0]

        # Only connect nearby nodes
        if abs(y1 - y2) < 250:
            connection_alpha = int(100 * (0.5 + 0.5 * math.sin(2 * math.pi * (t + i) / 2)))
            draw.line([(x1, y1), (x2, y2)], fill=(0, 217, 255, connection_alpha), width=2)

            # Data pulses on connections
            for pulse_num in range(2):
                pulse_progress = (t * 1.5 + pulse_num * 0.5) % 1
                pulse_x = x1 + (x2 - x1) * pulse_progress
                pulse_y = y1 + (y2 - y1) * pulse_progress

                draw.ellipse(
                    [(pulse_x - 8, pulse_y - 8), (pulse_x + 8, pulse_y + 8)],
                    fill=(16, 185, 129, 255)
                )

    # AI label (with glow)
    ai_label_x, ai_label_y = ai_start_x + 50, 100
    for offset in range(1, 5):
        draw.text((ai_label_x + offset, ai_label_y + offset), "AI MODEL",
                 font=small_font, fill=(0, 217, 255, 80))
    draw.text((ai_label_x, ai_label_y), "AI MODEL",
             font=small_font, fill=(0, 217, 255, 255))

    # === RIGHT SIDE: REVENUE CHARTS ===
    chart_x = width // 2 + 200
    chart_y_base = height - 150
    chart_width = 600
    chart_height = 400

    # Chart background box
    draw.rectangle(
        [(chart_x - 30, chart_y_base - chart_height - 30),
         (chart_x + chart_width + 30, chart_y_base + 30)],
        outline=(0, 217, 255, 100),
        width=2
    )

    # === BAR CHART (left side of chart area) ===
    bar_data = [
        ("Week 1", 100),
        ("Week 2", 250),
        ("Week 3", 450),
        ("Week 4", 750),
        ("Week 5", 1200),
    ]

    for i, (label, max_value) in enumerate(bar_data):
        bar_x = chart_x + 20 + i * 100

        # Animate bar growth
        if t > 1:
            bar_height = (chart_height * max_value / 1200) * min(1, (t - 1) / 5)
        else:
            bar_height = 0

        # Bar with glow
        draw.rectangle(
            [(bar_x, chart_y_base - bar_height),
             (bar_x + 70, chart_y_base)],
            fill=(16, 185, 129, 220),
            outline=(16, 185, 129, 255),
            width=2
        )

        # Value on top of bar
        if bar_height > 20:
            value_text = f"${int(max_value * (bar_height / (chart_height * max_value / 1200)))}K"
            draw.text(
                (bar_x + 10, chart_y_base - bar_height - 30),
                value_text,
                font=small_font,
                fill=(16, 185, 129, 200)
            )

    # === LINE CHART (right side) ===
    line_points = []
    line_values = [150, 300, 550, 900, 1400, 1800]

    for i, value in enumerate(line_values):
        x = chart_x + 320 + i * 50

        # Animate line growth
        if t > 1:
            progress = min(1, (t - 1) / 5)
            y = chart_y_base - (chart_height * value / 2000 * progress)
        else:
            y = chart_y_base

        line_points.append((x, y))

    # Draw line
    for i in range(len(line_points) - 1):
        x1, y1 = line_points[i]
        x2, y2 = line_points[i + 1]
        draw.line([(x1, y1), (x2, y2)], fill=(255, 215, 0, 200), width=3)

    # Draw points on line
    for x, y in line_points:
        if y < chart_y_base:
            draw.ellipse(
                [(x - 10, y - 10), (x + 10, y + 10)],
                fill=(255, 215, 0, 255),
                outline=(255, 255, 100, 255),
                width=2
            )

    # Axis labels
    draw.text((chart_x - 80, chart_y_base + 20), "$",
             font=medium_font, fill=(0, 217, 255, 150))

    # === CONNECTION LINE: AI → Revenue ===
    if t > 0.5:
        connection_alpha = int(150 * min(1, (t - 0.5) / 1))
        connection_x1 = ai_start_x + 500
        connection_y1 = height // 2
        connection_x2 = chart_x - 50
        connection_y2 = chart_y_base - chart_height // 2

        draw.line(
            [(connection_x1, connection_y1), (connection_x2, connection_y2)],
            fill=(0, 217, 255, connection_alpha),
            width=3
        )

        # Animated arrow/indicator on connection
        progress = (t - 0.5) / 2 % 1
        arrow_x = connection_x1 + (connection_x2 - connection_x1) * progress
        arrow_y = connection_y1 + (connection_y2 - connection_y1) * progress

        draw.ellipse(
            [(arrow_x - 15, arrow_y - 15), (arrow_x + 15, arrow_y + 15)],
            fill=(16, 185, 129, 255)
        )

    # === LARGE REVENUE TEXT (CENTER, TOP) ===
    if t > 1.5:
        revenue_alpha = min(255, int(255 * (t - 1.5) / 1.5))
        revenue = min(9999999, int(9999999 * (t - 1.5) / 10))

        revenue_text = f"${revenue:,}"
        rev_x, rev_y = width // 2 - 400, 80

        # Glow shadow
        for offset in range(1, 8):
            draw.text((rev_x + offset, rev_y + offset), revenue_text,
                     font=big_font, fill=(16, 185, 129, revenue_alpha // 5))
        # Main text
        draw.text((rev_x, rev_y), revenue_text,
                 font=big_font, fill=(16, 185, 129, revenue_alpha))

    # === TITLE TEXT (VERY LARGE) ===
    if t > 0.3:
        title_alpha = min(255, int(255 * (t - 0.3) / 1))
        title_x, title_y = width // 2 - 600, height - 180

        # Shadow/glow
        for offset in range(1, 6):
            draw.text((title_x + offset, title_y + offset), "AI REVENUE ENGINE",
                     font=medium_font, fill=(0, 217, 255, title_alpha // 4))
        # Main
        draw.text((title_x, title_y), "AI REVENUE ENGINE",
                 font=medium_font, fill=(0, 217, 255, title_alpha))

    return img

def generate_video():
    output_dir = Path("/tmp/makemoney_ai_charts")
    output_dir.mkdir(exist_ok=True)

    video_file = Path(__file__).parent / "hero-bots.mp4"
    fps = 30
    duration_seconds = 16
    total_frames = fps * duration_seconds

    print(f"Creating AI Revenue Chart video...")

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
