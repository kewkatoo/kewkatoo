"""Generates the animated project SVGs into ./assets (run from the repo root).
Works on any Python 3.8+ (no nested f-strings)."""
import os

OUT_DIR = "assets"
os.makedirs(OUT_DIR, exist_ok=True)

BG = "#090714"
CARD = "#0d0a1a"
STROKE = "#5b3df5"
GLOW = "#8b6cff"
TEXT = "#f5f3ff"
SUBTLE = "#20163b"

WIDTH = 1200
HEIGHT = 320


def svg_wrapper(title, inner_svg):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{title}">
  <defs>
    <linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#7c5cff"/>
      <stop offset="50%" stop-color="#5b3df5"/>
      <stop offset="100%" stop-color="#2b174f"/>
    </linearGradient>
    <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="100%" height="100%" rx="28" fill="{BG}"/>
  <rect x="10" y="10" width="{WIDTH - 20}" height="{HEIGHT - 20}" rx="24" fill="{CARD}" stroke="url(#borderGrad)" stroke-width="2"/>
  <text x="50%" y="48" text-anchor="middle" fill="{TEXT}" font-size="28" font-family="Inter, Segoe UI, Arial, sans-serif" font-weight="600">{title}</text>
  {inner_svg}
</svg>'''


def save(name, title, inner):
    with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
        f.write(svg_wrapper(title, inner))


# ---------- small helpers (replace the nested f-strings) ----------
def nodes(pts, r=10, stroke=GLOW, sw=2):
    return "".join(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{CARD}" stroke="{stroke}" stroke-width="{sw}"/>'
        for x, y in pts
    )


def spokes(cx, cy, pts, color=SUBTLE, sw=2):
    return "".join(
        f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" stroke="{color}" stroke-width="{sw}"/>'
        for x, y in pts
    )


def segs(segments, color=SUBTLE, sw=2):
    return "".join(
        f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" stroke="{color}" stroke-width="{sw}"/>'
        for a, b, c, d in segments
    )


def pulse(path, dur, r=4):
    return (
        f'<circle r="{r}" fill="{GLOW}" filter="url(#softGlow)">'
        f'<animateMotion dur="{dur}s" repeatCount="indefinite" path="{path}"/></circle>'
    )


# 1. AURA
aura_pts = [(220, 130), (320, 220), (440, 130), (760, 130), (880, 220), (980, 130)]
aura_dur = [2.2, 2.5, 1.9, 2.1, 2.6, 2.0]
aura = f'''
<g>
  <rect x="70" y="90" width="1060" height="180" rx="18" fill="none" stroke="{SUBTLE}" stroke-width="1.5"/>
  {spokes(600, 180, aura_pts)}
  {nodes(aura_pts)}
  <circle cx="600" cy="180" r="24" fill="none" stroke="{GLOW}" stroke-width="2.5" filter="url(#softGlow)"/>
  <circle cx="600" cy="180" r="8" fill="{GLOW}">
    <animate attributeName="r" values="7;10;7" dur="1.8s" repeatCount="indefinite"/>
  </circle>
  <circle cx="600" cy="180" r="36" fill="none" stroke="{STROKE}" stroke-width="2" opacity="0.8">
    <animate attributeName="r" values="36;56;36" dur="2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.8;0.15;0.8" dur="2s" repeatCount="indefinite"/>
  </circle>
  <circle cx="600" cy="180" r="50" fill="none" stroke="{STROKE}" stroke-width="1.5" opacity="0.5">
    <animate attributeName="r" values="50;74;50" dur="2.3s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.5;0.1;0.5" dur="2.3s" repeatCount="indefinite"/>
  </circle>
  {"".join(pulse(f"M 600 180 L {x} {y}", d) for (x, y), d in zip(aura_pts, aura_dur))}
</g>
'''
save("aura_anim.svg", "AURA — Privacy-First Voice AI Concierge", aura)

# 2. Adaptive Learning
g_nodes = [(320, 180), (430, 130), (430, 230), (560, 180), (690, 130), (690, 230), (820, 180)]
g_lines = [
    (320, 180, 430, 130), (320, 180, 430, 230),
    (430, 130, 560, 180), (430, 230, 560, 180),
    (560, 180, 690, 130), (560, 180, 690, 230),
    (690, 130, 820, 180), (690, 230, 820, 180),
]
adaptive = f'''
<g>
  <rect x="120" y="110" width="90" height="110" rx="10" fill="none" stroke="{GLOW}" stroke-width="2"/>
  <rect x="145" y="128" width="40" height="4" fill="{GLOW}" opacity="0.7"/>
  <rect x="145" y="142" width="50" height="4" fill="{GLOW}" opacity="0.55"/>
  <rect x="145" y="156" width="30" height="4" fill="{GLOW}" opacity="0.4"/>
  <rect x="990" y="110" width="90" height="110" rx="10" fill="none" stroke="{GLOW}" stroke-width="2"/>
  <circle cx="1035" cy="150" r="16" fill="none" stroke="{GLOW}" stroke-width="2"/>
  <path d="M1025 150 L1033 158 L1048 140" fill="none" stroke="{GLOW}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  {segs(g_lines)}
  {nodes(g_nodes, r=9, stroke=STROKE)}
  {pulse("M 150 165 L 320 180 L 430 130 L 560 180 L 690 230 L 820 180 L 1035 165", 3.2, r=5)}
</g>
'''
save("adaptive_learning_anim.svg", "AI Adaptive Learning Platform", adaptive)

# 3. Prosthetic Arm
particles = [(160, 80, 2.4, 0.1), (180, 100, 2.2, 0.5), (210, 90, 2.0, 0.8),
             (245, 110, 2.1, 1.1), (280, 140, 2.3, 1.5), (220, 180, 2.5, 1.8)]
particle_svg = "".join(
    f'<circle cx="{cx}" cy="{cy}" r="3" fill="{STROKE}">'
    f'<animate attributeName="opacity" values="0;1;0" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></circle>'
    for cx, cy, dur, begin in particles
)
prosthetic = f'''
<g transform="translate(250,65)">
  <path d="M160 170 C150 140,150 120,150 90 L150 55 M185 165 L180 75 M215 165 L215 62 M245 168 L255 85 M275 175 L295 110 M155 175 C175 210,235 210,270 180"
        fill="none" stroke="{GLOW}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  {particle_svg}
</g>
<line x1="560" y1="180" x2="838" y2="180" stroke="{SUBTLE}" stroke-width="3"/>
<circle cx="860" cy="180" r="22" fill="none" stroke="{GLOW}" stroke-width="3"/>
<circle cx="860" cy="180" r="6" fill="{GLOW}">
  <animate attributeName="r" values="6;10;6" dur="1.7s" repeatCount="indefinite"/>
</circle>
<rect x="820" y="140" width="80" height="80" rx="8" fill="none" stroke="{STROKE}" stroke-width="2">
  <animate attributeName="opacity" values="0.2;1;0.2" dur="2s" repeatCount="indefinite"/>
</rect>
'''
save("prosthetic_arm_anim.svg", "Intelligent Prosthetic Arm", prosthetic)

# 4. Song Recommendation
bars = [(170, 150, 60, 100, 130, 0.9), (205, 130, 100, 60, 150, 1.1), (240, 165, 30, 80, 140, 1.0),
        (275, 120, 120, 70, 145, 1.2), (310, 145, 70, 110, 125, 0.95)]
bar_svg = "".join(
    f'<rect x="{x}" y="{y}" width="18" height="{h}" rx="9" fill="{GLOW}">'
    f'<animate attributeName="height" values="{h};{h2};{h}" dur="{d}s" repeatCount="indefinite"/>'
    f'<animate attributeName="y" values="{y};{y2};{y}" dur="{d}s" repeatCount="indefinite"/></rect>'
    for x, y, h, h2, y2, d in bars
)
rec_pts = [(860, 120), (940, 180), (860, 240), (1020, 180)]
song = f'''
<g>
  {bar_svg}
  <path d="M390 180 C430 110,470 250,510 180 S590 110,630 180 S710 250,750 180"
        fill="none" stroke="{STROKE}" stroke-width="4" stroke-linecap="round">
    <animate attributeName="d" dur="2s" repeatCount="indefinite"
      values="M390 180 C430 110,470 250,510 180 S590 110,630 180 S710 250,750 180;M390 180 C430 140,470 220,510 180 S590 140,630 180 S710 220,750 180;M390 180 C430 110,470 250,510 180 S590 110,630 180 S710 250,750 180"/>
  </path>
  {segs([(760, 180, 860, 120), (760, 180, 940, 180), (760, 180, 860, 240), (940, 180, 1020, 180)])}
  {nodes(rec_pts, r=11)}
  {pulse("M 760 180 L 860 120 L 940 180 L 1020 180", 2.8, r=5)}
</g>
'''
save("song_recommendation_anim.svg", "Song Recommendation Framework", song)

# 5. Smart Helmet
sensor_pts = [(780, 100), (860, 140), (930, 200), (820, 245)]
helmet = f'''
<g transform="translate(290,75)">
  <path d="M80 140 C80 65,140 30,220 30 C300 30,360 65,360 140 L360 170 L80 170 Z" fill="none" stroke="{GLOW}" stroke-width="4"/>
  <rect x="120" y="105" width="200" height="18" rx="9" fill="{SUBTLE}"/>
  <circle cx="220" cy="140" r="14" fill="none" stroke="{STROKE}" stroke-width="3"/>
  <path d="M220 140 L330 110 A120 120 0 0 0 220 20 Z" fill="{GLOW}" opacity="0.15">
    <animateTransform attributeName="transform" type="rotate" from="0 220 140" to="360 220 140" dur="3.5s" repeatCount="indefinite"/>
  </path>
</g>
{spokes(650, 170, sensor_pts)}
{nodes(sensor_pts, r=7)}
{pulse("M 650 170 L 780 100 L 860 140 L 930 200 L 820 245", 2.4)}
'''
save("smart_helmet_anim.svg", "Smart Helmet", helmet)

# 6. IoT Bus Detection
windows = "".join(
    f'<rect x="{x}" y="60" width="50" height="35" rx="6" fill="none" stroke="{STROKE}" stroke-width="2"/>'
    for x in (20, 85, 150, 215)
)
bus = f'''
<g transform="translate(180,95)">
  <rect x="0" y="40" width="300" height="110" rx="18" fill="none" stroke="{GLOW}" stroke-width="4"/>
  {windows}
  <circle cx="65" cy="165" r="16" fill="none" stroke="{GLOW}" stroke-width="3"/>
  <circle cx="235" cy="165" r="16" fill="none" stroke="{GLOW}" stroke-width="3"/>
  <rect x="-10" y="30" width="320" height="130" rx="20" fill="none" stroke="{STROKE}" stroke-width="2">
    <animate attributeName="opacity" values="0.2;1;0.2" dur="1.8s" repeatCount="indefinite"/>
  </rect>
</g>
<line x1="600" y1="100" x2="600" y2="250" stroke="{GLOW}" stroke-width="3" opacity="0.9">
  <animate attributeName="x1" values="560;640;560" dur="2s" repeatCount="indefinite"/>
  <animate attributeName="x2" values="560;640;560" dur="2s" repeatCount="indefinite"/>
</line>
<line x1="740" y1="175" x2="920" y2="175" stroke="{SUBTLE}" stroke-width="2"/>
<circle cx="920" cy="175" r="22" fill="none" stroke="{GLOW}" stroke-width="3"/>
<circle cx="980" cy="175" r="12" fill="{GLOW}" opacity="0.95"/>
{pulse("M 500 175 L 740 175 L 920 175 L 980 175", 2.2, r=5)}
'''
save("bus_detection_anim.svg", "Real-Time IoT Bus Detection", bus)

print("All SVGs generated in assets/")
