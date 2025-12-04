#!/usr/bin/env python3
"""Render a performance & observability flow PNG without relying on Cairo.

Generates docs/developer-guides/assets/perf-flow.png replicating the SVG layout.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path('docs/developer-guides/assets/perf-flow.png')
WIDTH, HEIGHT = 1600, 420

COLORS = {
    'bg': (245, 247, 250, 255),
    'text_dark': (24, 36, 51, 255),
    'white': (255, 255, 255, 255),
    'box1': (11, 95, 255, 255),
    'box2': (0, 122, 90, 255),
    'box3': (106, 0, 168, 255),
    'box4': (201, 94, 0, 255),
    'box5': (189, 0, 75, 255),
    'note': (245, 247, 250, 255),
    'note_border': (139, 161, 183, 255),
    'arrow': (24, 36, 51, 255),
    'breach': (189, 0, 75, 255),
}

def load_font(size):
    try:
        return ImageFont.truetype('Helvetica.ttf', size)
    except Exception:
        try:
            return ImageFont.truetype('Arial.ttf', size)
        except Exception:
            return ImageFont.load_default()

def draw_rounded(draw: ImageDraw.ImageDraw, xy, fill, outline=None, width=2, radius=12):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def text_block(draw, x, y, lines, font_main, line_spacing=4, fill=COLORS['white']):
    cy = y
    for i, line in enumerate(lines):
        draw.text((x, cy), line, font=font_main, fill=fill)
        cy += font_main.size + line_spacing

def arrow(draw, x0, y0, x1, y1, color, head_size=10):
    draw.line((x0, y0, x1, y1), fill=color, width=3)
    # Simple triangular arrow head
    hx = x1
    hy = y1
    draw.polygon([(hx, hy), (hx - head_size, hy - head_size/2), (hx - head_size, hy + head_size/2)], fill=color)

def breach_path(draw):
    # Approximate curved path using polyline segments
    points = [
        (1390, 180), (1390, 210), (1350, 230), (1280, 250), (1210, 280), (1200, 310)
    ]
    draw.line(points, fill=COLORS['breach'], width=3)
    # Arrow head at end
    x1, y1 = points[-1]
    draw.polygon([(x1, y1), (x1 + 12, y1 - 6), (x1 + 12, y1 + 6)], fill=COLORS['breach'])

def main():
    img = Image.new('RGBA', (WIDTH, HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    font_title = load_font(22)
    font_small = load_font(16)
    font_label = load_font(18)

    # Boxes coordinates
    boxes = [
        ((20, 60, 270, 180), COLORS['box1'], ["Operation", "Endpoint / job / FHIR op"]),
        ((300, 60, 550, 180), COLORS['box2'], ["Expectation Entry", "p50 / p95 / max + rationale"]),
        ((580, 60, 880, 180), COLORS['box3'], ["Deployment Emits", "Structured Log + Metrics + Trace", "Correlation IDs / dimensions"]),
        ((910, 60, 1210, 180), COLORS['box4'], ["Validator Asserts", "Compare live latency vs targets", "Fail fast in CI / nightly"]),
        ((1240, 60, 1580, 180), COLORS['box5'], ["Dashboard & Taxonomy", "Trend, Percentiles, Error buckets", "Actionable + drill-down"]),
    ]
    for (x0, y0, x1, y1), color, lines in boxes:
        draw_rounded(draw, (x0, y0, x1, y1), fill=color, outline=color)
        # Write lines
        text_block(draw, x0 + 15, y0 + 30, lines[:1], font_title)
        if len(lines) > 1:
            text_block(draw, x0 + 15, y0 + 65, lines[1:], font_small)

    # Arrows between boxes
    arrow(draw, 270, 120, 300, 120, COLORS['arrow'])
    arrow(draw, 550, 120, 580, 120, COLORS['arrow'])
    arrow(draw, 880, 120, 910, 120, COLORS['arrow'])
    arrow(draw, 1210, 120, 1240, 120, COLORS['arrow'])

    # Breach path
    breach_path(draw)
    draw.text((1210, 330), "Breach ⇒ Story / Alert / Escalation", font=font_label, fill=COLORS['text_dark'])

    # PERF-001 Baseline Note
    draw_rounded(draw, (20, 250, 690, 370), fill=COLORS['note'], outline=COLORS['note_border'], radius=10)
    note_lines = [
        ("PERF-001 Baseline", font_label),
        ("Delegates concrete thresholds to registry (expectations.yaml)", font_small),
        ("Allows agile target evolution without NFR re-approval", font_small),
        ("Governance: changes tracked via Conventional Commits", font_small),
    ]
    y = 270
    for line, fnt in note_lines:
        draw.text((40, y), line, font=fnt, fill=COLORS['text_dark'])
        y += fnt.size + 6

    # Legend
    draw_rounded(draw, (730, 250, 1260, 370), fill=COLORS['note'], outline=COLORS['note_border'], radius=10)
    legend_lines = [
        ("Legend", font_label),
        ("Blue: Source Operation", font_small),
        ("Green: Declarative Target (registry)", font_small),
        ("Purple: Telemetry Emission", font_small),
        ("Orange: Validation Stage", font_small),
        ("Pink: Insights & Actions", font_small),
    ]
    y = 270
    for line, fnt in legend_lines:
        draw.text((750, y), line, font=fnt, fill=COLORS['text_dark'])
        y += fnt.size + 6

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    print(f"Wrote {OUT}")

if __name__ == '__main__':
    main()
