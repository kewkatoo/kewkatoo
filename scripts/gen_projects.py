"""Story-driven animated project cards (pure SVG + CSS keyframes, no JS, no external assets).
Run from the repo root:  python scripts/gen_projects.py
Output filenames are unchanged, so README references keep working."""
import os
from html import escape

OUT_DIR = "assets"
W, H = 1200, 320

BG, CARD = "#090714", "#0d0a1a"
P1, P2, P3 = "#8b6cff", "#5b3df5", "#a78bfa"
SUB, LINE, TXT, MUT, CREAM = "#20163b", "#2a2340", "#f5f3ff", "#8b86a0", "#f5efe3"
SURF, SURF2 = "#141024", "#1b1730"
GREEN, AMBER, RED = "#4ade80", "#fbbf24", "#f87171"
SKIN, SKIN_D = "#e8b894", "#d39e78"
SANS = "Inter,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
EASE = "cubic-bezier(.45,0,.2,1)"


class Scene:
    """Collects CSS keyframes. Every animated element shares one loop length (dur)."""

    def __init__(self, dur):
        self.dur, self.css, self.n, self.defs = dur, [], 0, []

    def kf(self, steps, ease=EASE):
        """steps: [(t_seconds, {o,x,y,r,s,sx,sy,fill,stroke,e})]. State persists between steps.
        Returns the class name. First/last frames are padded so the loop is seamless."""
        self.n += 1
        name = f"a{self.n}"
        steps = sorted(steps, key=lambda s: s[0])
        if steps[0][0] > 0:
            steps.insert(0, (0, dict(steps[0][1])))
        if steps[-1][0] < self.dur:
            steps.append((self.dur, {}))
        keys = set()
        for _, p in steps:
            keys |= {k for k in p if k != "e"}
        use_tf = bool(keys & {"x", "y", "r", "s", "sx", "sy"})
        state = dict(o=1, x=0, y=0, r=0, s=1, sx=1, sy=1, fill=None, stroke=None)
        first = {}
        for _, p in steps:
            for k, v in p.items():
                if k != "e" and k not in first:
                    first[k] = v
        state.update(first)
        out, last_pct = [], -1.0
        for i, (t, p) in enumerate(steps):
            state.update({k: v for k, v in p.items() if k != "e"})
            pct = round(t / self.dur * 100, 3)
            if pct <= last_pct:
                pct = round(last_pct + 0.002, 3)
            if i == len(steps) - 1:
                pct = 100
            last_pct = pct
            decl = []
            if use_tf:
                decl.append(f"transform:translate({state['x']:g}px,{state['y']:g}px) rotate({state['r']:g}deg) "
                            f"scale({state['s'] * state['sx']:g},{state['s'] * state['sy']:g})")
            if "o" in keys:
                decl.append(f"opacity:{state['o']:g}")
            if "fill" in keys:
                decl.append(f"fill:{state['fill']}")
            if "stroke" in keys:
                decl.append(f"stroke:{state['stroke']}")
            if i < len(steps) - 1:
                decl.append(f"animation-timing-function:{p.get('e', ease)}")
            out.append(f"{pct:g}%{{{';'.join(decl)}}}")
        self.css.append(f"@keyframes {name}{{{''.join(out)}}}.{name}{{animation:{name} {self.dur}s infinite}}")
        return name

    def g(self, content, steps, ease=EASE, extra=""):
        return f'<g class="{self.kf(steps, ease)}"{extra}>{content}</g>'

    def el(self, tag, attrs, steps, ease=EASE):
        return f'<{tag} class="{self.kf(steps, ease)}" {attrs}/>'


def T(x, y, s, size=13, fill=TXT, w=600, anchor="middle", fam=None, extra=""):
    f = f' font-family="{fam}"' if fam else ""
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{w}" '
            f'fill="{fill}"{f}{extra}>{escape(s)}</text>')


def at(x, y, inner):
    return f'<g transform="translate({x},{y})">{inner}</g>'


def hold(t0, t1, **p):
    """Two identical keyframes = state held between t0 and t1."""
    return [(t0, dict(p)), (t1, dict(p))]


def wrap(title, body, sc, defs=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(title)}">
<defs>
<linearGradient id="bdr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7c5cff"/><stop offset=".5" stop-color="#5b3df5"/><stop offset="1" stop-color="#2b174f"/></linearGradient>
<clipPath id="inner"><rect x="12" y="12" width="{W - 24}" height="{H - 24}" rx="22"/></clipPath>
{defs}
</defs>
<style>text{{font-family:{SANS}}}{"".join(sc.css)}</style>
<rect width="{W}" height="{H}" rx="28" fill="{BG}"/>
<rect x="10" y="10" width="{W - 20}" height="{H - 20}" rx="24" fill="{CARD}" stroke="url(#bdr)" stroke-width="2"/>
<text x="600" y="47" text-anchor="middle" fill="{TXT}" font-size="25" font-weight="600">{escape(title)}</text>
<g clip-path="url(#inner)">{body}</g>
</svg>'''


REG = {}


def save(name, title, body, sc, defs=""):
    REG[name] = dict(title=title, body=body, css="".join(sc.css), defs=defs)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
        f.write(wrap(title, body, sc, defs))


# =====================================================================================
# 1. AURA, voice request -> hub -> butler's tablet
# =====================================================================================
def aura():
    s = Scene(9)
    defs = f'''
<linearGradient id="hood" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6d4fe0"/><stop offset="1" stop-color="#3b2a9e"/></linearGradient>
<linearGradient id="puck" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#120e20"/><stop offset=".5" stop-color="#241d3f"/><stop offset="1" stop-color="#120e20"/></linearGradient>
<radialGradient id="scr" cx=".5" cy=".3" r=".9"><stop offset="0" stop-color="#1b1535"/><stop offset="1" stop-color="#0b0916"/></radialGradient>
<filter id="blur6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>'''
    b = []
    # soft floor glow
    b.append(f'<ellipse cx="600" cy="300" rx="520" ry="26" fill="#2b1b66" opacity=".22" filter="url(#blur6)"/>')

    # --- person (headset, curly hair, glasses) -------------------------------------
    breathe = s.g(f'''
<path d="M62 312 C62 250 96 228 134 221 L206 221 C244 228 278 250 278 312 Z" fill="url(#hood)"/>
<path d="M134 221 Q170 250 206 221 L206 230 Q170 262 134 230Z" fill="#3b2a9e"/>
<path d="M156 238 L152 270 M184 238 L188 270" stroke="#cfc8e8" stroke-width="2" stroke-linecap="round"/>
<path d="M154 196 L154 228 Q170 242 186 228 L186 196Z" fill="{SKIN_D}"/>
<ellipse cx="131" cy="164" rx="6" ry="9" fill="{SKIN_D}"/><ellipse cx="209" cy="164" rx="6" ry="9" fill="{SKIN_D}"/>
<ellipse cx="170" cy="160" rx="38" ry="44" fill="{SKIN}"/>
<g fill="#15101f"><circle cx="142" cy="128" r="15"/><circle cx="158" cy="116" r="16"/><circle cx="178" cy="113" r="16"/><circle cx="196" cy="119" r="15"/><circle cx="208" cy="135" r="13"/><circle cx="133" cy="143" r="11"/><circle cx="210" cy="150" r="9"/><path d="M134 142 Q170 112 206 142 Q196 132 170 130 Q146 132 134 142Z"/></g>
<path d="M146 146 q10 -5 20 0 M174 146 q10 -5 20 0" stroke="#15101f" stroke-width="2.4" fill="none" stroke-linecap="round"/>
<ellipse cx="156" cy="160" rx="3" ry="3.4" fill="#15101f"/><ellipse cx="184" cy="160" rx="3" ry="3.4" fill="#15101f"/>
<rect x="140" y="148" width="29" height="23" rx="8" fill="none" stroke="#1d1830" stroke-width="2.4"/><rect x="171" y="148" width="29" height="23" rx="8" fill="none" stroke="#1d1830" stroke-width="2.4"/>
<path d="M169 158 h2" stroke="#1d1830" stroke-width="2.4"/>
<path d="M170 164 q-3 8 2 10" stroke="{SKIN_D}" stroke-width="2.2" fill="none" stroke-linecap="round"/>
''', [(0, dict(y=0)), (2.2, dict(y=-1.5)), (4.5, dict(y=0)), (6.7, dict(y=-1.5)), (9, dict(y=0))])
    b.append(breathe)
    # mouth (talks 0.9 -> 2.5)
    mouth_steps = [(0, dict(sy=.25))]
    t = 0.85
    while t < 2.45:
        mouth_steps += [(t, dict(sy=.25)), (t + .11, dict(sy=1.5)), (t + .22, dict(sy=.5)), (t + .31, dict(sy=1.1))]
        t += .36
    mouth_steps += [(2.7, dict(sy=.25))]
    b.append(at(170, 183, s.g(f'<ellipse cx="0" cy="0" rx="8" ry="4.2" fill="#7a2f3b"/><ellipse cx="0" cy="1.2" rx="4.5" ry="1.8" fill="#d8707c"/>', mouth_steps)))
    # headset
    b.append(f'''<path d="M129 150 Q129 103 170 101 Q211 103 211 150" stroke="#d9d3ee" stroke-width="4.5" fill="none" stroke-linecap="round"/>
<rect x="203" y="144" width="15" height="28" rx="7" fill="#2a2340" stroke="{P1}" stroke-width="1.6"/><rect x="122" y="144" width="15" height="28" rx="7" fill="#2a2340" stroke="#4a3d78" stroke-width="1.4"/>
<path d="M214 170 Q218 204 194 196" stroke="#d9d3ee" stroke-width="3" fill="none" stroke-linecap="round"/>
<ellipse cx="190" cy="195" rx="9" ry="6" fill="#15101f" stroke="{P1}" stroke-width="1.5"/><ellipse cx="188" cy="193.5" rx="4" ry="2" fill="#fff" opacity=".35"/>''')
    # blink
    b.append(s.g(f'<rect x="138" y="152" width="64" height="12" fill="{SKIN}" opacity="0"/>', [(0, dict(o=0)), (9, {})]))

    # --- sound waves -------------------------------------------------------------------
    arc = f'<path d="M0 -26 Q19 0 0 26" stroke="{P1}" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M-12 -16 Q0 0 -12 16" stroke="{P3}" stroke-width="2.4" fill="none" stroke-linecap="round" opacity=".6"/>'
    for i in range(5):
        t0 = 0.95 + i * .32
        b.append(at(206, 190, s.g(arc, [(0, dict(o=0, x=0, s=.5)), (t0, dict(o=0, x=0, s=.5)), (t0 + .12, dict(o=1, x=8, s=.7, e="linear")),
                                        (t0 + 1.35, dict(o=.0, x=122, s=1.7)), (9, dict(o=0))])))

    # --- hub (processing) ---------------------------------------------------------------
    i_hub = len(b)
    hub = f'''<path d="M504 178 L504 214 Q504 236 560 236 Q616 236 616 214 L616 178 Z" fill="url(#puck)" stroke="{LINE}"/>
<ellipse cx="560" cy="178" rx="56" ry="16" fill="#211a3b" stroke="#3a3158"/>
<ellipse cx="560" cy="178" rx="44" ry="10.5" fill="none" stroke="#3a3158" stroke-width="3"/>
<circle cx="560" cy="178" r="3" fill="#cfc8e8" opacity=".5"/>
<path d="M522 214 q38 10 76 0" stroke="#33294f" stroke-width="2" fill="none"/>'''
    b.append(hub)
    ring = f'<ellipse cx="560" cy="178" rx="44" ry="10.5" fill="none" stroke="{P1}" stroke-width="3.2" stroke-linecap="round" stroke-dasharray="52 200" style="animation:spin 1.1s linear infinite"/>'
    b.append(s.g(ring, [(0, dict(o=0)), (2.3, dict(o=0)), (2.5, dict(o=1)), (3.45, dict(o=1)), (3.7, dict(o=0)), (9, {})]))
    b.append(s.g(f'<ellipse cx="560" cy="178" rx="46" ry="12" fill="{P1}" filter="url(#blur6)"/>',
                 [(0, dict(o=0)), (2.2, dict(o=0)), (2.7, dict(o=.55)), (3.5, dict(o=.35)), (3.9, dict(o=0)), (9, {})]))
    # ripple when the voice arrives
    b.append(at(560, 178, s.g(f'<ellipse cx="0" cy="0" rx="48" ry="12" fill="none" stroke="{P3}" stroke-width="2"/>',
                              [(0, dict(o=0, s=.8)), (2.3, dict(o=0, s=.8)), (2.4, dict(o=.8, s=.9)), (3.0, dict(o=0, s=1.7)), (9, dict(o=0, s=1.7))])))
    # intent chip with a water drop
    chip = f'''<rect x="-34" y="-18" width="68" height="36" rx="18" fill="{SURF2}" stroke="{P1}" stroke-width="1.6"/>
<path d="M0 -11 C-7 -3 -10 1 -10 5 A10 10 0 0 0 10 5 C10 1 7 -3 0 -11Z" fill="{P1}"/><path d="M-4 4 q0 4 4 5" stroke="#fff" stroke-width="1.6" fill="none" stroke-linecap="round" opacity=".7"/>'''
    chip_el = (at(560, 132, s.g(chip, [(0, dict(o=0, x=0, y=14, s=.3)), (3.3, dict(o=0, x=0, y=14, s=.3)), (3.6, dict(o=1, x=0, y=0, s=1.12)),
                                     (3.8, dict(o=1, x=0, y=0, s=1)), (4.1, dict(o=1, x=140, y=-26, s=1, e="linear")), (4.55, dict(o=1, x=310, y=-30, s=1, e="linear")),
                                     (4.95, dict(o=1, x=420, y=24, s=.9)), (5.1, dict(o=0, x=430, y=46, s=.5)), (9, dict(o=0))])))
    b[i_hub:] = ['<g transform="translate(-150,0)">' + ''.join(b[i_hub:]) + '</g>']
    b.append(f'<path d="M478 148 Q600 66 706 118" stroke="{LINE}" stroke-width="2" stroke-dasharray="3 7" fill="none" opacity=".8"/>')

    # --- butler + tablet ------------------------------------------------------------------
    i_but = len(b)
    butler = f'''
<path d="M790 312 C790 258 818 236 850 228 L910 228 C942 236 970 258 970 312 Z" fill="#17122a" stroke="{LINE}"/>
<path d="M862 228 L880 270 L898 228 Z" fill="#f1ecf8"/><path d="M846 228 L862 228 L874 252 Z M914 228 L898 228 L886 252 Z" fill="#241d3f"/>
<path d="M870 238 l-16 -8 v16z M890 238 l16 -8 v16z" fill="#6d4fe0"/><rect x="873" y="233" width="14" height="11" rx="3" fill="#8b6cff"/>
<path d="M870 200 L870 230 Q880 238 890 230 L890 200Z" fill="#c78f6c"/>
<ellipse cx="846" cy="172" rx="5" ry="8" fill="#c78f6c"/><ellipse cx="914" cy="172" rx="5" ry="8" fill="#c78f6c"/>
<ellipse cx="880" cy="170" rx="33" ry="38" fill="#d8a583"/>
<path d="M847 168 Q844 128 880 126 Q916 128 913 168 Q906 146 880 144 Q854 146 847 168Z" fill="#dcd7ea"/>
<path d="M850 160 q-4 12 0 20 M910 160 q4 12 0 20" stroke="#dcd7ea" stroke-width="5" fill="none" stroke-linecap="round"/>
<path d="M862 156 q8 -5 16 0 M882 156 q8 -5 16 0" stroke="#dcd7ea" stroke-width="3" fill="none" stroke-linecap="round"/>
<circle cx="870" cy="166" r="2.6" fill="#1d1830"/><circle cx="890" cy="166" r="2.6" fill="#1d1830"/>
<path d="M866 186 Q880 178 894 186 Q880 192 866 186Z" fill="#dcd7ea"/>
<path d="M872 196 q8 4 16 0" stroke="#8a5a4a" stroke-width="2" fill="none" stroke-linecap="round"/>'''
    nod = s.g(butler, [(0, dict(y=0)), (5.6, dict(y=0)), (5.95, dict(y=5)), (6.35, dict(y=0)), (9, {})])
    b.append(nod)
    # arm + hand
    b.append(f'<path d="M944 244 Q962 262 958 282" stroke="#17122a" stroke-width="26" fill="none" stroke-linecap="round"/><path d="M944 244 Q962 262 958 282" stroke="{LINE}" stroke-width="1" fill="none"/>')
    # tablet
    b.append(f'<rect x="946" y="108" width="212" height="170" rx="16" fill="#0a0814" stroke="#3a3158" stroke-width="2.4"/><rect x="956" y="118" width="192" height="150" rx="9" fill="url(#scr)"/>')
    b.append(f'<circle cx="1052" cy="113" r="1.8" fill="#3a3158"/>')
    # idle list
    rows = ""
    for i in range(3):
        y = 164 + i * 32
        rows += f'<circle cx="978" cy="{y}" r="9" fill="#2a2340"/><rect x="994" y="{y - 8}" width="{86 - i * 10}" height="6" rx="3" fill="#2f2650"/><rect x="994" y="{y + 2}" width="{56 - i * 6}" height="5" rx="2.5" fill="#241d3f"/><rect x="1108" y="{y - 6}" width="30" height="12" rx="6" fill="#241d3f"/>'
    b.append(f'<rect x="966" y="128" width="60" height="7" rx="3.5" fill="#2f2650"/><circle cx="1134" cy="131" r="4" fill="{P1}" opacity=".7"/>')
    b.append(s.g(rows, [(0, dict(o=1)), (4.9, dict(o=1)), (5.2, dict(o=.28)), (7.3, dict(o=.28)), (7.7, dict(o=1)), (9, {})]))
    # screen glow when the notification lands
    b.append(s.g(f'<rect x="956" y="118" width="192" height="150" rx="9" fill="none" stroke="{P1}" stroke-width="2"/>', [(0, dict(o=0)), (5.0, dict(o=0)), (5.2, dict(o=1)), (5.6, dict(o=.0)), (9, {})]))
    # notification card
    card = f'''<rect x="0" y="0" width="172" height="104" rx="12" fill="{SURF2}" stroke="#3a3158"/>
<circle cx="24" cy="26" r="14" fill="{P2}"/><path d="M24 17 C19 23 17 26 17 29 A7 7 0 0 0 31 29 C31 26 29 23 24 17Z" fill="#fff"/>
{T(46, 24, "Water requested", 12.5, TXT, 700, "start")}{T(46, 40, "Living room", 10.5, MUT, 500, "start")}'''
    btn = f'<rect x="12" y="62" width="148" height="30" rx="15" class="btn"/>'
    b.append(at(966, 130, s.g(card, [(0, dict(o=0, y=-26)), (4.95, dict(o=0, y=-26)), (5.3, dict(o=1, y=0)), (6.95, dict(o=1, y=0)), (7.4, dict(o=0, y=-14)), (9, dict(o=0, y=-14))])))
    b.append(at(966, 130, s.g(
        s.el("rect", f'x="12" y="62" width="148" height="30" rx="15"', [(0, dict(fill=P1)), (5.85, dict(fill=P1)), (6.0, dict(fill=GREEN)), (9, dict(fill=GREEN))], ) +
        T(86, 82, "Accept", 12.5, "#0d0a1a", 700, extra=' class="' + s.kf([(0, dict(o=1)), (5.9, dict(o=1)), (6.0, dict(o=0)), (9, dict(o=0))]) + '"') +
        T(86, 82, "Accepted ✓", 12.5, "#0d0a1a", 700, extra=' class="' + s.kf([(0, dict(o=0)), (5.95, dict(o=0)), (6.05, dict(o=1)), (9, dict(o=1))]) + '"'),
        [(0, dict(o=0, y=-26)), (4.95, dict(o=0, y=-26)), (5.3, dict(o=1, y=0)), (6.95, dict(o=1, y=0)), (7.4, dict(o=0, y=-14)), (9, dict(o=0, y=-14))])))
    # tap ripple on the button
    b.append(at(1052, 222, s.g(f'<circle r="16" fill="#fff"/>', [(0, dict(o=0, s=.1)), (5.8, dict(o=0, s=.1)), (5.85, dict(o=.55, s=.3)), (6.3, dict(o=0, s=1.4)), (9, dict(o=0, s=1.4))])))
    # fingertip that taps the Accept button
    finger = (f'<path d="M-9 60 C-10 30 -10 10 -7 0 C-4 -6 4 -6 7 0 C10 10 10 30 9 60Z" fill="{SKIN}" stroke="#b9855f" stroke-width="1.2"/>'
              f'<ellipse cx="0" cy="6" rx="4.6" ry="6" fill="#f6dcc8"/><path d="M-9 34 H9" stroke="#c99571" stroke-width="1" opacity=".6"/>')
    b.append(at(1052, 220, s.g(finger, [(0, dict(o=0, x=34, y=80)), (5.3, dict(o=0, x=34, y=80)), (5.55, dict(o=1, x=10, y=34)), (5.82, dict(o=1, x=0, y=8)), (5.9, dict(o=1, x=0, y=0, s=.95)),
                                        (6.2, dict(o=1, x=2, y=24, s=1)), (6.5, dict(o=0, x=34, y=80)), (9, dict(o=0, x=34, y=80))])))

    b[i_but:] = ['<g transform="translate(-230,0)">' + ''.join(b[i_but:]) + '</g>']
    b.append('<g transform="translate(-150,0)">' + chip_el + '</g>')
    css = "@keyframes spin{to{stroke-dashoffset:-252}}"
    s.css.append(css)
    save("aura_anim.svg", "AURA \u2014 Voice AI Concierge", "".join(b), s, defs)



# =====================================================================================
# 2. PREPPER, an adaptive quiz UI with a cursor
# =====================================================================================
def prepper():
    D = 10.0
    s = Scene(D)
    defs = f'''<filter id="blur10" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
<linearGradient id="btn" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7c5cff"/><stop offset="1" stop-color="#5b3df5"/></linearGradient>'''
    qs = [
        ("Which gas makes up most of Earth\u2019s atmosphere?", ["Oxygen", "Nitrogen", "Argon", "Carbon dioxide"], 1),
        ("What is the derivative of sin(x)?", ["cos(x)", "\u2212sin(x)", "tan(x)", "\u2212cos(x)"], 0),
        ("Which data structure follows FIFO order?", ["Stack", "Tree", "Queue", "Graph"], 2),
    ]
    X0, Y0, WW, HH = 150, 70, 900, 226
    cx, cw = 174, 852
    ow, oh = 416, 38
    ox = [cx, cx + ow + 20]
    oy = [166, 212]
    nxt = (976, 272)
    b = [f'<ellipse cx="600" cy="190" rx="420" ry="90" fill="#3b1f7a" opacity=".35" filter="url(#blur10)"/>']
    b.append(f'<rect x="{X0}" y="{Y0}" width="{WW}" height="{HH}" rx="16" fill="#0f0c1c" stroke="#2f2650" stroke-width="1.5"/>')
    b.append(f'<path d="M{X0} {Y0 + 30} V{Y0 + 16} a16 16 0 0 1 16 -16 H{X0 + WW - 16} a16 16 0 0 1 16 16 V{Y0 + 30}Z" fill="{SURF}"/>')
    b.append(f'<circle cx="{X0 + 20}" cy="{Y0 + 15}" r="4.5" fill="#3a3158"/><circle cx="{X0 + 36}" cy="{Y0 + 15}" r="4.5" fill="#3a3158"/><circle cx="{X0 + 52}" cy="{Y0 + 15}" r="4.5" fill="#3a3158"/>')
    b.append(f'<rect x="470" y="{Y0 + 6}" width="260" height="18" rx="9" fill="#0f0c1c"/>' + T(600, Y0 + 19, "prepper.app/practice", 10.5, MUT, 500))
    # progress segments
    SW, SG = 273, 16
    seg_starts = [i * 10 / 3 for i in range(3)]
    for i in range(3):
        x = cx + i * (SW + SG)
        b.append(f'<rect x="{x}" y="112" width="{SW}" height="6" rx="3" fill="#241d3f"/>')
        t_fill = seg_starts[i] + 2.15
        b.append(at(x, 112, s.g(f'<rect x="0" y="0" width="{SW}" height="6" rx="3" fill="{P1}"/>',
                                [(0, dict(sx=0)), (t_fill, dict(sx=0)), (t_fill + .4, dict(sx=1)), (9.7, dict(sx=1)), (9.95, dict(sx=0)), (D, dict(sx=0))])))
    # level pips (adaptive difficulty)
    b.append(T(cx + cw - 82, 138, "level", 11, MUT, 500, "end"))
    for i in range(3):
        steps = [(0, dict(fill="#2a2340"))] if i else [(0, dict(fill=P1))]
        if i:
            tl = seg_starts[i - 1] + 2.3
            steps += [(tl, dict(fill="#2a2340")), (tl + .25, dict(fill=P1)), (9.7, dict(fill=P1)), (9.95, dict(fill="#2a2340"))]
        b.append(s.el("circle", f'cx="{cx + cw - 60 + i * 16}" cy="134" r="5"', steps))
    # questions
    for qi, (q, opts, ans) in enumerate(qs):
        s0 = seg_starts[qi]
        grp = [T(cx, 150, q, 18, TXT, 700, "start")]
        sel_t = s0 + 1.25
        for k, label in enumerate(opts):
            x, y = ox[k % 2], oy[k // 2]
            grp.append(f'<rect x="{x}" y="{y}" width="{ow}" height="{oh}" rx="11" fill="{SURF}" stroke="{LINE}"/>')
            grp.append(f'<circle cx="{x + 22}" cy="{y + 19}" r="11" fill="#241d3f"/>' + T(x + 22, y + 23.5, "ABCD"[k], 12, "#cfc8e8", 700))
            grp.append(T(x + 44, y + 24.5, label, 14.5, "#e6e0f5", 500, "start"))
        chosen = ans
        x, y = ox[chosen % 2], oy[chosen // 2]
        sel = (f'<rect x="{x}" y="{y}" width="{ow}" height="{oh}" rx="11" fill="#2a1d5e" stroke="{P1}" stroke-width="2"/>'
               f'<circle cx="{x + 22}" cy="{y + 19}" r="11" fill="{P1}"/>' + T(x + 22, y + 23.5, "ABCD"[chosen], 12, "#fff", 700) +
               T(x + 44, y + 24.5, opts[chosen], 14.5, "#fff", 600, "start"))
        grp.append(s.g(sel, [(0, dict(o=0)), (sel_t, dict(o=0)), (sel_t + .12, dict(o=1)), (s0 + 2.62, dict(o=1)), (s0 + 2.63, dict(o=0)), (D, dict(o=0))]))
        ok = (f'<rect x="{x}" y="{y}" width="{ow}" height="{oh}" rx="11" fill="#12301f" stroke="{GREEN}" stroke-width="2"/>'
              f'<circle cx="{x + 22}" cy="{y + 19}" r="11" fill="{GREEN}"/><path d="M{x + 17} {y + 19.5} l4 4 l7 -8" stroke="#0d0a1a" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' +
               T(x + 44, y + 24.5, opts[chosen], 14.5, "#fff", 600, "start"))
        grp.append(s.g(ok, [(0, dict(o=0)), (sel_t + .55, dict(o=0)), (sel_t + .75, dict(o=1)), (s0 + 2.62, dict(o=1)), (s0 + 2.63, dict(o=0)), (D, dict(o=0))]))
        if qi == 0:
            steps = [(0, dict(o=1, x=0)), (s0 + 2.35, dict(o=1, x=0)), (s0 + 2.7, dict(o=0, x=-60)), (9.62, dict(o=0, x=60)), (D, dict(o=1, x=0))]
        else:
            steps = [(0, dict(o=0, x=60)), (s0 - .33, dict(o=0, x=60)), (s0, dict(o=1, x=0)), (s0 + 2.35, dict(o=1, x=0)), (s0 + 2.7, dict(o=0, x=-60)), (D, dict(o=0, x=-60))]
        b.append(s.g("".join(grp), steps))
    # next button
    bx, by, bw, bh = 926, 258, 100, 28
    dis_steps, press = [(0, dict(fill="#241d3f"))], []
    for i in range(3):
        s0 = seg_starts[i]
        dis_steps += [(s0 + 1.25, dict(fill="#241d3f")), (s0 + 1.45, dict(fill=P2)), (s0 + 2.5, dict(fill=P2)), (s0 + 2.75, dict(fill="#241d3f"))]
    b.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="14" fill="#241d3f" class="{s.kf(dis_steps)}"/>')
    b.append(T(bx + 44, by + 18.5, "Next", 13, "#fff", 700) + f'<path d="M{bx + 68} {by + 14} h9 m-4 -4 l4 4 l-4 4" stroke="#fff" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    # button press ring
    ring_steps = [(0, dict(o=0, s=1))]
    for i in range(3):
        t = seg_starts[i] + 2.12
        ring_steps += [(t, dict(o=0, s=1)), (t + .05, dict(o=.7, s=1)), (t + .45, dict(o=0, s=1.35))]
    b.append(at(bx + bw / 2, by + bh / 2, s.g(f'<rect x="{-bw / 2}" y="{-bh / 2}" width="{bw}" height="{bh}" rx="14" fill="none" stroke="{P3}" stroke-width="2"/>', ring_steps)))
    # cursor
    tgt = [((ox[1] + 330, oy[0] + 20), None), ((ox[0] + 330, oy[0] + 20), None), ((ox[0] + 330, oy[1] + 20), None)]
    cur = [(0, dict(x=1000, y=150, s=1))]
    for i in range(3):
        s0 = seg_starts[i]
        px, py = tgt[i][0]
        cur += [(s0 + .45, dict(x=cur[-1][1]["x"], y=cur[-1][1]["y"], s=1)), (s0 + 1.15, dict(x=px, y=py, s=1)),
                (s0 + 1.22, dict(x=px, y=py, s=.82)), (s0 + 1.34, dict(x=px, y=py, s=1)),
                (s0 + 1.95, dict(x=nxt[0] - 4, y=nxt[1] - 4, s=1)), (s0 + 2.06, dict(x=nxt[0] - 4, y=nxt[1] - 4, s=.82)), (s0 + 2.2, dict(x=nxt[0] - 4, y=nxt[1] - 4, s=1)),
                (s0 + 2.75, dict(x=980, y=170, s=1))]
    cur += [(9.7, dict(x=980, y=170, s=1)), (D, dict(x=1000, y=150, s=1))]
    arrow = f'<path d="M0 0 L0 18 L4.8 13.8 L8 21 L10.8 19.8 L7.6 12.8 L13.6 12.8 Z" fill="#fff" stroke="#0d0a1a" stroke-width="1.3" stroke-linejoin="round"/>'
    b.append(s.g(arrow, cur))
    save("adaptive_learning_anim.svg", "Prepper \u2014 AI Adaptive Learning", "".join(b), s, defs)



# =====================================================================================
# 3. PROSTHETIC ARM, scan -> reach -> grasp -> lift -> release
# =====================================================================================
def prosthetic():
    D = 10.0
    s = Scene(D)
    BX, BY, R = 860, 252, 36                     # apple
    K0 = (500, 138)                              # knuckle line at rest (world)
    K = 1.4                                      # hand scale
    LX, LY = K0[0] - 80 * K, K0[1] + 42 * K      # camera lens (world, at rest)
    GX, GY = BX - 10 - K0[0], (BY - R - 3 - 28 * K) - K0[1]   # grasp offset
    defs = f'''
<linearGradient id="metal" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6a6196"/><stop offset=".35" stop-color="#3b3358"/><stop offset="1" stop-color="#1a1430"/></linearGradient>
<linearGradient id="metalD" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4c4570"/><stop offset=".4" stop-color="#2a2345"/><stop offset="1" stop-color="#150f28"/></linearGradient>
<linearGradient id="sleeve" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2e2850"/><stop offset=".5" stop-color="#1c1736"/><stop offset="1" stop-color="#110c22"/></linearGradient>
<radialGradient id="apple" cx=".35" cy=".3" r=".85"><stop offset="0" stop-color="#ff8a8a"/><stop offset=".55" stop-color="#e03a55"/><stop offset="1" stop-color="#8f1d3b"/></radialGradient>
<linearGradient id="cone" gradientUnits="userSpaceOnUse" x1="{LX}" y1="{LY}" x2="{BX - R - 20}" y2="{BY}"><stop offset="0" stop-color="{P1}" stop-opacity=".6"/><stop offset="1" stop-color="{P1}" stop-opacity=".06"/></linearGradient>
<linearGradient id="fadeL" gradientUnits="userSpaceOnUse" x1="40" y1="0" x2="330" y2="0"><stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient>
<mask id="mfade" maskUnits="userSpaceOnUse" x="0" y="0" width="1200" height="320"><rect width="1200" height="320" fill="url(#fadeL)"/></mask>
<clipPath id="conec"><polygon points="{LX},{LY} {BX - R - 24},{BY - R - 24} {BX - R - 24},{BY + R + 12}"/></clipPath>
<filter id="blur5" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>'''
    b = []
    b.append(f'<rect x="560" y="288" width="620" height="12" fill="#171230"/><rect x="560" y="288" width="620" height="1.5" fill="#33295a"/>')
    b.append(f'<ellipse cx="{BX}" cy="290" rx="170" ry="10" fill="#3b1f7a" opacity=".35" filter="url(#blur5)"/>')
    sh = s.g(f'<ellipse cx="0" cy="0" rx="{R}" ry="6" fill="#000" opacity=".55"/>',
             [(0, dict(o=0, sx=.4)), (.9, dict(o=0, sx=.4)), (1.0, dict(o=1, sx=1)), (6.2, dict(o=1, sx=1)), (7.0, dict(o=.45, sx=.7)), (7.7, dict(o=.45, sx=.7)), (8.3, dict(o=1, sx=1)), (9.0, dict(o=1, sx=1)), (9.5, dict(o=0, sx=1)), (D, dict(o=0, sx=.4))])
    b.append(at(BX, 289, sh))
    top = BY - R
    apple = (f'<path d="M{BX - 2} {top + 5} q-1 -13 7 -20" stroke="#6b4423" stroke-width="3.4" fill="none" stroke-linecap="round"/>'
             f'<path d="M{BX + 5} {top - 8} q16 -11 28 -2 q-9 13 -28 2Z" fill="#4ade80"/>'
             f'<circle cx="{BX}" cy="{BY}" r="{R}" fill="url(#apple)"/><ellipse cx="{BX}" cy="{top + 3}" rx="10" ry="4.5" fill="#7a1631"/>'
             f'<ellipse cx="{BX - 13}" cy="{BY - 12}" rx="7" ry="12" fill="#fff" opacity=".26" transform="rotate(25 {BX - 13} {BY - 12})"/>')
    LIFT = 46
    b.append(s.g(apple, [(0, dict(o=0, y=-95)), (.4, dict(o=0, y=-95)), (.5, dict(o=1, y=-95, e="cubic-bezier(.5,0,1,.6)")), (.95, dict(o=1, y=0)), (1.05, dict(o=1, y=-9, e="ease-out")), (1.18, dict(o=1, y=0)),
                         (6.2, dict(y=0)), (7.0, dict(y=-LIFT)), (7.7, dict(y=-LIFT)), (8.3, dict(y=0)), (9.0, dict(o=1, y=0)), (9.5, dict(o=0, y=0)), (9.6, dict(o=0, y=-95)), (D, dict(o=0, y=-95))]))
    poly = f"{LX},{LY} {BX - R - 24},{BY - R - 24} {BX - R - 24},{BY + R + 12}"
    b.append(s.g(f'<polygon points="{poly}" fill="url(#cone)"/>', [(0, dict(o=0)), (1.4, dict(o=0)), (1.8, dict(o=1)), (3.0, dict(o=1)), (3.4, dict(o=0)), (D, dict(o=0))]))
    vscan = f'<rect x="-3" y="130" width="6" height="190" fill="{P3}" opacity=".9"/><rect x="-30" y="130" width="30" height="190" fill="{P1}" opacity=".22"/>'
    b.append('<g clip-path="url(#conec)">' + s.g(vscan, [(0, dict(o=0, x=LX)), (1.8, dict(o=0, x=LX)), (1.9, dict(o=1, x=LX)), (3.0, dict(o=1, x=BX - R - 24)), (3.1, dict(o=0, x=BX - R - 24)), (D, dict(o=0, x=LX))], ease="linear") + '</g>')
    bw = 2 * R + 28
    bx0, by0 = BX - bw / 2, BY - bw / 2
    br = ""
    for (cx_, cy_, dx, dy) in [(bx0, by0, 1, 1), (bx0 + bw, by0, -1, 1), (bx0, by0 + bw, 1, -1), (bx0 + bw, by0 + bw, -1, -1)]:
        br += f'<path d="M{cx_ + dx * 18} {cy_} H{cx_} V{cy_ + dy * 18}" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    def brk(col):
        return f'<g transform="translate({-BX},{-BY})"><g style="color:{col}">{br}</g></g>'
    b.append(at(BX, BY, s.g(brk(P3), [(0, dict(o=0, s=1.5)), (2.0, dict(o=0, s=1.5)), (2.6, dict(o=1, s=1)), (2.8, dict(o=1, s=1.06)), (3.0, dict(o=1, s=1)), (5.1, dict(o=1, s=1)), (5.3, dict(o=0, s=1)), (D, dict(o=0, s=1))])))
    b.append(at(BX, BY, s.g(brk(GREEN), [(0, dict(o=0, s=1, y=0)), (5.9, dict(o=0, s=1.12, y=0)), (6.1, dict(o=1, s=1, y=0)), (6.2, dict(o=1, s=1, y=0)), (7.0, dict(o=1, s=1, y=-LIFT)), (7.3, dict(o=0, s=1, y=-LIFT)), (7.31, dict(o=0, s=1, y=0)), (D, dict(o=0))])))
    hscan = f'<rect x="{bx0 + 4}" y="-2" width="{bw - 8}" height="4" rx="2" fill="{P3}"/><rect x="{bx0 + 4}" y="-28" width="{bw - 8}" height="26" fill="{P1}" opacity=".22"/>'
    b.append(s.g(hscan, [(0, dict(o=0, y=by0)), (2.2, dict(o=0, y=by0)), (2.3, dict(o=1, y=by0 + 4)), (2.8, dict(o=1, y=by0 + bw - 4)), (3.1, dict(o=1, y=by0 + 6)), (3.3, dict(o=0, y=by0 + 6)), (D, dict(o=0, y=by0))], ease="linear"))
    chip = f'<rect x="-47" y="-12" width="94" height="23" rx="11.5" fill="{SURF2}" stroke="{P1}"/>' + T(0, 3.8, "apple 98%", 11.5, TXT, 600)
    b.append(at(BX, by0 - 16, s.g(chip, [(0, dict(o=0, y=6)), (2.9, dict(o=0, y=6)), (3.15, dict(o=1, y=0)), (5.1, dict(o=1, y=0)), (5.3, dict(o=0, y=0)), (D, dict(o=0))])))

    # ---------------- hand (local origin = knuckle line, drawn at scale K) ----------------
    def seg(L, w, dark=False):
        g = "metalD" if dark else "metal"
        return (f'<rect x="0" y="{-w / 2}" width="{L}" height="{w}" rx="{w / 2}" fill="url(#{g})" stroke="#0e0a1c" stroke-width="1"/>'
                f'<rect x="4" y="{-w / 2 + 2}" width="{L - 8}" height="2" rx="1" fill="#fff" opacity=".16"/>'
                f'<circle cx="0" cy="0" r="{w / 2 - 3}" fill="#120d24" stroke="{P1}" stroke-width="1.2"/><circle cx="0" cy="0" r="1.8" fill="{P3}"/>')

    def finger(y0, lens, widths, a_open, a_close, t_close, t_open, dark):
        steps = lambda k: [(0, dict(r=a_open[k])), (t_close, dict(r=a_open[k])), (t_close + .85, dict(r=a_close[k])), (t_open, dict(r=a_close[k])), (t_open + .5, dict(r=a_open[k])), (D, dict(r=a_open[k]))]
        s3 = s.g(seg(lens[2], widths[2], dark) + f'<rect x="{lens[2] - 9}" y="{-widths[2] / 2 + 2}" width="9" height="{widths[2] - 4}" rx="4" fill="#0f0a1d" opacity=".9"/>', steps(2))
        s2 = s.g(seg(lens[1], widths[1], dark) + f'<g transform="translate({lens[1]},0)">{s3}</g>', steps(1))
        s1 = s.g(seg(lens[0], widths[0], dark) + f'<g transform="translate({lens[0]},0)">{s2}</g>', steps(0))
        return f'<g transform="translate(0,{y0})">{s1}</g>'

    hand = []
    th = lambda k, op, cl: [(0, dict(r=op[k])), (5.1, dict(r=op[k])), (5.95, dict(r=cl[k])), (8.3, dict(r=cl[k])), (8.8, dict(r=op[k])), (D, dict(r=op[k]))]
    t_op, t_cl = (118, 6), (80, -15)
    t2 = s.g(seg(30, 15) + '<rect x="21" y="-5.5" width="9" height="11" rx="4" fill="#0f0a1d"/>', th(1, t_op, t_cl))
    t1 = s.g(seg(38, 17) + f'<g transform="translate(38,0)">{t2}</g>', th(0, t_op, t_cl))
    hand.append(f'<g transform="translate(-40,22)">{t1}</g>')
    hand.append(finger(-15, (38, 29, 24), (16, 14, 12.5), (3, 5, 3), (52, 8, 46), 5.2, 8.3, True))
    hand.append(finger(-7, (40, 30, 25), (17, 15, 13), (4, 6, 4), (55, 8, 48), 5.12, 8.3, False))
    hand.append(finger(1, (38, 28, 24), (17, 15, 13), (4, 6, 4), (57, 8, 48), 5.05, 8.3, False))
    hand.append(f'<rect x="-520" y="-25" width="400" height="54" rx="14" fill="url(#sleeve)" stroke="#0e0a1c"/>'
                f'<rect x="-520" y="-17" width="400" height="3" fill="{P1}" opacity=".5"/>'
                + "".join(f'<rect x="{-500 + i * 46}" y="-6" width="26" height="2" rx="1" fill="#fff" opacity=".07"/><rect x="{-488 + i * 46}" y="6" width="26" height="2" rx="1" fill="#fff" opacity=".05"/>' for i in range(8)))
    hand.append(f'<rect x="-146" y="-31" width="30" height="66" rx="9" fill="url(#metalD)" stroke="#0e0a1c"/><rect x="-140" y="-22" width="4" height="48" rx="2" fill="{P1}" opacity=".7"/>')
    hand.append(f'<rect x="-120" y="-26" width="124" height="54" rx="15" fill="url(#metal)" stroke="#0e0a1c" stroke-width="1.2"/>'
                f'<rect x="-104" y="-19" width="78" height="5" rx="2.5" fill="{P1}" opacity=".85"/><rect x="-104" y="-19" width="78" height="5" rx="2.5" fill="{P3}" class="{s.kf([(0, dict(o=.2)), (2.5, dict(o=.9)), (5, dict(o=.2)), (7.5, dict(o=.9)), (D, dict(o=.2))])}"/>'
                f'<path d="M-92 4 H-30 M-92 12 H-46" stroke="#0e0a1c" stroke-width="1.4" opacity=".7"/><circle cx="-10" cy="-8" r="2" fill="#120d24"/><circle cx="-10" cy="14" r="2" fill="#120d24"/>')
    hand.append(f'<path d="M-100 26 H-60 L-64 42 H-96 Z" fill="url(#metalD)" stroke="#0e0a1c" stroke-width="1.2"/>'
                f'<ellipse cx="-80" cy="42" rx="14" ry="5.5" fill="#0a0716" stroke="#6a6196" stroke-width="1.4"/><ellipse cx="-80" cy="42" rx="8" ry="3.4" fill="#201845"/>'
                f'<ellipse cx="-82" cy="41.2" rx="3" ry="1.2" fill="#fff" opacity=".7"/>'
                + s.el("circle", 'cx="-66" cy="32" r="2.4"', [(0, dict(fill="#3a3158")), (1.3, dict(fill="#3a3158")), (1.5, dict(fill=RED)), (3.3, dict(fill=RED)), (3.5, dict(fill=GREEN)), (9.6, dict(fill=GREEN)), (9.8, dict(fill="#3a3158")), (D, dict(fill="#3a3158"))]))
    hg = s.g(f'<g transform="scale({K})">{"".join(hand)}</g>',
             [(0, dict(x=0, y=0)), (3.4, dict(x=0, y=0)), (4.4, dict(x=GX - 90, y=GY - 24)), (5.05, dict(x=GX, y=GY)),
              (6.2, dict(x=GX, y=GY)), (7.0, dict(x=GX, y=GY - LIFT)), (7.7, dict(x=GX, y=GY - LIFT)),
              (8.3, dict(x=GX, y=GY)), (8.8, dict(x=GX, y=GY)), (9.7, dict(x=0, y=0)), (D, dict(x=0, y=0))])
    b.append(f'<g mask="url(#mfade)"><g transform="translate({K0[0]},{K0[1]})">{hg}</g></g>')
    save("prosthetic_arm_anim.svg", "Intelligent Prosthetic Arm", "".join(b), s, defs)


def BR(by, r):
    return by - r + 4



# =====================================================================================
# 4. SONG RECOMMENDATION, player -> scan -> similar tracks panel
# =====================================================================================
def songs():
    D = 9.0
    s = Scene(D)
    defs = f'''
<linearGradient id="art1" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7c5cff"/><stop offset=".55" stop-color="#c04bd8"/><stop offset="1" stop-color="#ff7aa8"/></linearGradient>
<linearGradient id="art2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3b82f6"/><stop offset="1" stop-color="#8b6cff"/></linearGradient>
<linearGradient id="art3" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f59e0b"/><stop offset="1" stop-color="#ef4466"/></linearGradient>
<linearGradient id="art4" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#14b8a6"/><stop offset="1" stop-color="#6366f1"/></linearGradient>
<linearGradient id="art5" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ec4899"/><stop offset="1" stop-color="#5b3df5"/></linearGradient>
<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{P1}" stop-opacity="0"/><stop offset="1" stop-color="{P3}" stop-opacity=".55"/></linearGradient>
<clipPath id="plist"><rect x="596" y="112" width="550" height="176"/></clipPath>
<clipPath id="wavec"><rect x="84" y="186" width="452" height="72"/></clipPath>
<linearGradient id="fadeb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#141024" stop-opacity="0"/><stop offset="1" stop-color="#141024"/></linearGradient>
<linearGradient id="fadet" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#141024"/><stop offset="1" stop-color="#141024" stop-opacity="0"/></linearGradient>
<filter id="blur8" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>'''
    b = [f'<ellipse cx="330" cy="200" rx="300" ry="90" fill="#3b1f7a" opacity=".3" filter="url(#blur8)"/>']
    # ---- player ----
    b.append(f'<rect x="60" y="72" width="500" height="226" rx="18" fill="{SURF}" stroke="{LINE}"/>')
    b.append(f'<rect x="84" y="92" width="100" height="100" rx="14" fill="url(#art1)"/>'
             f'<circle cx="134" cy="138" r="30" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="2"/><circle cx="134" cy="138" r="19" fill="none" stroke="#fff" stroke-opacity=".3" stroke-width="2"/>'
             f'<circle cx="134" cy="138" r="8" fill="#fff" fill-opacity=".85"/><path d="M84 176 q26 -20 50 -4 t50 -6 V192 H84Z" fill="#1b0f40" opacity=".35"/>')
    b.append(T(208, 116, "Midnight Drive", 20, TXT, 700, "start") + T(208, 138, "Neon Harbor", 13, MUT, 500, "start"))
    b.append(T(208, 166, "Synthwave \u00b7 124 bpm", 11.5, "#a29cb8", 500, "start"))
    # equalizer icon
    for i, base in enumerate([.6, 1, .45]):
        st = [(0, dict(sy=base))]
        t = .0
        k = 0
        while t < D - .6:
            t += .38 + .05 * i
            st.append((t, dict(sy=[.3, 1, .55, .85][(k + i) % 4])))
            k += 1
        st.append((D, dict(sy=base)))
        b.append(at(500 + i * 9, 130, s.g(f'<rect x="0" y="-22" width="5" height="22" rx="2.5" fill="{P1}"/>', st)))
    # finding-similar chip
    chip = (f'<rect x="0" y="0" width="150" height="26" rx="13" fill="{SURF2}" stroke="{P1}"/>'
            f'<circle cx="17" cy="12" r="5.5" fill="none" stroke="{P3}" stroke-width="1.8"/><path d="M21 16 l4.5 4.5" stroke="{P3}" stroke-width="1.8" stroke-linecap="round"/>'
            + T(32, 17, "finding similar", 11.5, TXT, 600, "start"))
    b.append(at(386, 150, s.g(chip, [(0, dict(o=0, y=6)), (1.15, dict(o=0, y=6)), (1.4, dict(o=1, y=0)), (2.95, dict(o=1, y=0)), (3.2, dict(o=0, y=0)), (D, dict(o=0, y=0))])))
    # waveform bars (progressive fill)
    import math
    N, x0, pitch = 56, 84, 452 / 56
    for c in range(N // 2):
        inner = ""
        for j in (0, 1):
            i = c * 2 + j
            h = 10 + 46 * abs(math.sin(i * .47 + .4) * math.cos(i * .15 + .3)) + 4 * math.sin(i * 1.7)
            h = max(8, min(58, h))
            inner += f'<rect x="{x0 + i * pitch + 1:.1f}" y="{224 - h / 2:.1f}" width="{pitch - 3.2:.1f}" height="{h:.1f}" rx="2"/>'
        t_on = (c * 2 / N - .14) / .74 * 8.4
        if t_on <= 0:
            st = [(0, dict(fill=P1))]
        else:
            st = [(0, dict(fill="#2f2650")), (t_on, dict(fill="#2f2650")), (t_on + .1, dict(fill=P1)), (8.75, dict(fill=P1)), (8.95, dict(fill="#2f2650")), (D, dict(fill="#2f2650"))]
            if False:
                pass
        if t_on <= 0:
            st = [(0, dict(fill=P1)), (8.75, dict(fill=P1)), (D, dict(fill=P1))]
        b.append(s.g(inner, st))
    # playhead
    ph = f'<rect x="-1" y="190" width="2" height="68" rx="1" fill="#fff"/><circle cx="0" cy="190" r="4.5" fill="#fff"/>'
    xa, xb = x0 + .14 * 452, x0 + .88 * 452
    b.append(s.g(ph, [(0, dict(o=1, x=xa)), (8.4, dict(o=1, x=xb)), (8.65, dict(o=0, x=xb)), (8.8, dict(o=0, x=xa)), (D, dict(o=1, x=xa))], ease="linear"))
    # scanning beam over waveform
    b.append('<g clip-path="url(#wavec)">' + s.g(f'<rect x="-90" y="186" width="90" height="72" fill="url(#beam)"/><rect x="-2" y="186" width="3" height="72" fill="{P3}"/>',
                                              [(0, dict(o=0, x=84)), (1.3, dict(o=0, x=84)), (1.45, dict(o=1, x=130)), (2.9, dict(o=1, x=600)), (3.0, dict(o=0, x=600)), (D, dict(o=0, x=84))], ease="linear") + '</g>')
    # controls
    b.append('<path d="M250 271 v14 M250 278 l12 -7 v14z" stroke="#cfc8e8" fill="#cfc8e8" stroke-width="2" stroke-linejoin="round"/>'
             '<path d="M370 271 v14 M370 278 l-12 -7 v14z" stroke="#cfc8e8" fill="#cfc8e8" stroke-width="2" stroke-linejoin="round"/>')
    b.append(f'<circle cx="310" cy="278" r="16" fill="{P2}"/><rect x="304.5" y="271.5" width="4.4" height="13" rx="1.6" fill="#fff"/><rect x="311.5" y="271.5" width="4.4" height="13" rx="1.6" fill="#fff"/>')
    b.append('<path d="M98 272 h16 l-4 -4 m4 4 l-4 4 M98 283 h16 l-4 -4 m4 4 l-4 4" stroke="#6b6585" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append('<path d="M520 284 C508 276 513 266 520 272 C527 266 532 276 520 284Z" fill="none" stroke="#6b6585" stroke-width="1.8" stroke-linejoin="round"/>')
    # ---- recommendations panel ----
    rows = [("Neon Skyline", "Kairo", "97%", "art2"), ("After Hours Drift", "Lumen", "95%", "art3"), ("Midnight Static", "Velvet Echo", "93%", "art4"),
            ("Pulse Theory", "Orbit 9", "91%", "art5"), ("Afterglow", "Solenne", "89%", "art2")]
    panel = [f'<rect x="596" y="72" width="550" height="226" rx="18" fill="{SURF}" stroke="{LINE}"/>',
             T(620, 100, "Similar tracks", 15, TXT, 700, "start"),
             f'<rect x="1020" y="84" width="102" height="22" rx="11" fill="#241d3f"/>' + T(1071, 99, "MFCC match", 11.5, P3, 600)]
    lst = []
    for i, (ti, ar, pc, art) in enumerate(rows):
        y = 118 + i * 48
        r = f'<rect x="608" y="{y}" width="526" height="44" rx="12" fill="none"/>'
        if i == 1:
            r += s.g(f'<rect x="608" y="{y}" width="526" height="44" rx="12" fill="#2a1d5e" stroke="{P1}" stroke-width="1.6"/>', [(0, dict(o=0)), (4.3, dict(o=0)), (4.6, dict(o=1)), (6.4, dict(o=1)), (6.8, dict(o=0)), (D, dict(o=0))])
        r += f'<rect x="618" y="{y + 4}" width="36" height="36" rx="8" fill="url(#{art})"/>'
        r += T(668, y + 19, ti, 14, TXT, 650, "start") + T(668, y + 35, ar, 11.5, MUT, 500, "start") + T(1118, y + 27, pc, 14, P3, 700, "end")
        if i == 1:
            r += s.g(f'<circle cx="636" cy="{y + 22}" r="13" fill="#0d0a1a" fill-opacity=".55"/><path d="M632 {y + 15} l11 7 l-11 7z" fill="#fff"/>', [(0, dict(o=0)), (4.4, dict(o=0)), (4.7, dict(o=1)), (6.4, dict(o=1)), (6.8, dict(o=0)), (D, dict(o=0))])
        t_in = 3.1 + i * .13
        lst.append(s.g(r, [(0, dict(o=0, x=26)), (t_in, dict(o=0, x=26)), (t_in + .4, dict(o=1, x=0)), (7.7, dict(o=1, x=0)), (7.95, dict(o=0, x=0)), (D, dict(o=0, x=26))]))
    ghost = (f'<rect x="596" y="72" width="550" height="226" rx="18" fill="none" stroke="{LINE}" stroke-dasharray="4 6"/>' + T(620, 100, "similar tracks", 14, "#4a4268", 600, "start"))
    for i in range(4):
        y = 124 + i * 44
        ghost += f'<rect x="620" y="{y}" width="34" height="34" rx="8" fill="#171229"/><rect x="668" y="{y + 5}" width="{150 + (i % 2) * 40}" height="8" rx="4" fill="#171229"/><rect x="668" y="{y + 20}" width="80" height="7" rx="3.5" fill="#141024"/>'
    b.append(ghost)
    scroll = s.g("".join(lst), [(0, dict(y=0)), (5.4, dict(y=0)), (6.4, dict(y=-44)), (6.9, dict(y=-44)), (7.5, dict(y=0)), (D, dict(y=0))])
    panel.append(f'<g clip-path="url(#plist)">{scroll}</g>')
    panel.append('<rect x="600" y="262" width="542" height="26" fill="url(#fadeb)"/><rect x="600" y="112" width="542" height="12" fill="url(#fadet)"/>')
    b.append(s.g("".join(panel), [(0, dict(o=0, x=640)), (2.55, dict(o=0, x=640)), (2.7, dict(o=1, x=600)), (3.35, dict(o=1, x=0, e="cubic-bezier(.2,.8,.2,1)")), (7.6, dict(o=1, x=0)), (8.35, dict(o=0, x=640)), (D, dict(o=0, x=640))]))
    save("song_recommendation_anim.svg", "Song Recommendation Framework", "".join(b), s, defs)



# =====================================================================================
# 5. SMART HELMET, radar zones + HUD SAFE / WARNING / DANGER + alcohol sensor
# =====================================================================================
def helmet():
    import math
    D = 9.0
    s = Scene(D)
    SX, SY = 572, 158                      # radar origin (visor)
    A1, A2 = -5, 40                        # fan angles (deg, +ve = downward)
    RN, RF, RM = 169, 327, 530             # danger / warning / safe radii
    defs = f'''
<linearGradient id="shell" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3a2f6e"/><stop offset="1" stop-color="#17122c"/></linearGradient>
<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0916"/><stop offset="1" stop-color="#34237a"/></linearGradient>
<linearGradient id="jacket" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a2152"/><stop offset="1" stop-color="#120d26"/></linearGradient>
<linearGradient id="carb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a4fa0"/><stop offset="1" stop-color="#241d4a"/></linearGradient>
<linearGradient id="road" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b1632"/><stop offset="1" stop-color="#0e0a1c"/></linearGradient>
<radialGradient id="redg" cx=".35" cy=".6" r=".7"><stop offset="0" stop-color="{RED}" stop-opacity=".35"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>
<clipPath id="scn"><rect x="360" y="60" width="820" height="250"/></clipPath>'''
    def sector(r1, r2, a1=A1, a2=A2):
        p = lambda r, a: (SX + r * math.cos(math.radians(a)), SY + r * math.sin(math.radians(a)))
        x1, y1 = p(r2, a1); x2, y2 = p(r2, a2); x3, y3 = p(r1, a2); x4, y4 = p(r1, a1)
        return f"M{x1:.1f} {y1:.1f} A{r2} {r2} 0 0 1 {x2:.1f} {y2:.1f} L{x3:.1f} {y3:.1f} A{r1} {r1} 0 0 0 {x4:.1f} {y4:.1f}Z"
    zones = [("safe", RF + 3, RM, GREEN, [(0, 0), (1.3, 0), (1.5, 1), (2.7, 1), (2.9, 0), (6.9, 0), (7.1, 1), (7.8, 1), (8.0, 0)]),
             ("warn", RN, RF, AMBER, [(0, 0), (2.7, 0), (2.9, 1), (4.3, 1), (4.5, 0), (6.2, 0), (6.4, 1), (6.9, 1), (7.1, 0)]),
             ("dang", 40, RN, RED, [(0, 0), (4.3, 0), (4.5, 1), (6.2, 1), (6.4, 0)])]
    b = []
    # surroundings
    b.append(f'<rect x="380" y="282" width="800" height="20" fill="url(#road)"/><rect x="380" y="281" width="800" height="1.5" fill="#33295a"/>')
    road_kf = "@keyframes road{0%{stroke-dashoffset:0}49%{stroke-dashoffset:-480}55.5%{stroke-dashoffset:-510}66.6%{stroke-dashoffset:-510}100%{stroke-dashoffset:-720}}"
    s.css.append(road_kf)
    b.append(f'<line x1="380" y1="292" x2="1180" y2="292" stroke="#3a3158" stroke-width="3" stroke-dasharray="30 30" style="animation:road {D}s linear infinite"/>')
    b.append(s.g('<rect x="380" y="60" width="800" height="240" fill="url(#redg)"/>', [(0, dict(o=0)), (4.4, dict(o=0)), (4.7, dict(o=.9)), (5.1, dict(o=.45)), (5.5, dict(o=.9)), (6.0, dict(o=.45)), (6.4, dict(o=0)), (D, dict(o=0))]))
    # radar fan
    for name, r1, r2, col, act in zones:
        d = sector(r1, r2)
        b.append(f'<path d="{d}" fill="{col}" fill-opacity=".07" stroke="{col}" stroke-opacity=".28" stroke-width="1.2" stroke-dasharray="3 5"/>')
        b.append(s.g(f'<path d="{d}" fill="{col}" fill-opacity=".26"/>', [(t, dict(o=v)) for t, v in act] + [(D, dict(o=0))]))
    sweep = (f'<path d="M0 0 L{RM} 0 L{RM} {-RM * .12:.0f}Z" fill="{P1}" opacity=".30"/><line x1="0" y1="0" x2="{RM}" y2="0" stroke="{P3}" stroke-width="1.8" opacity=".9"/>')
    sw = []
    for i in range(3):
        sw += [(i * 3, dict(r=A1)), (i * 3 + 1.5, dict(r=A2))]
    sw.append((D, dict(r=A1)))
    b.append(at(SX, SY, s.g(sweep, sw)))
    # ping rings at the origin
    for t0 in (0.2, 3.2, 6.2):
        b.append(at(SX, SY, s.g(f'<circle r="26" fill="none" stroke="{P3}" stroke-width="1.6"/>', [(0, dict(o=0, s=.4)), (t0, dict(o=0, s=.4)), (t0 + .1, dict(o=.8, s=.5)), (t0 + 1.4, dict(o=0, s=2.6)), (D, dict(o=0, s=2.6))])))

    # ---- car (rear-left origin, ground line y=0) ----
    car_keys = [(0, 1215), (1.0, 1215), (1.05, 1190), (2.8, 889), (4.4, 720), (5.1, 688), (5.8, 688), (6.3, 720), (7.0, 889), (8.2, 1215), (D, 1215)]
    car = (f'<ellipse cx="86" cy="1" rx="86" ry="5" fill="#000" opacity=".5"/>'
           f'<path d="M2 -18 L2 -34 Q2 -40 10 -41 L40 -44 L62 -62 Q66 -66 74 -66 L116 -66 Q124 -66 130 -60 L148 -44 L162 -41 Q170 -39 170 -30 L170 -18 Q170 -14 164 -14 L6 -14 Q2 -14 2 -18Z" fill="url(#carb)" stroke="#0e0a1c" stroke-width="1.2"/>'
           f'<path d="M64 -58 L74 -61 L114 -61 Q119 -61 123 -57 L134 -46 L54 -46Z" fill="#150f33"/><path d="M94 -61 L98 -61 L90 -46 L86 -46Z" fill="#6a5cc8" opacity=".35"/>'
           f'<path d="M6 -28 H166" stroke="#0e0a1c" stroke-width="1" opacity=".6"/><rect x="74" y="-33" width="14" height="3" rx="1.5" fill="#0e0a1c" opacity=".6"/>'
           f'<rect x="158" y="-38" width="10" height="7" rx="3" fill="#fff6cf"/><rect x="1" y="-37" width="7" height="9" rx="2" fill="#7a1631"/>'
           + s.g('<circle cx="4" cy="-33" r="14" fill="%s" filter="url(#blurR)"/><rect x="1" y="-37" width="7" height="9" rx="2" fill="#ff5a6e"/>' % RED, [(0, dict(o=0)), (3.9, dict(o=0)), (4.2, dict(o=1)), (5.8, dict(o=1)), (6.0, dict(o=0)), (D, dict(o=0))]) +
           ''.join(f'<g transform="translate({cx},-14)"><circle r="14" fill="#0e0a1c"/><g style="animation:whl 1.2s linear infinite"><circle r="8" fill="#2a2345"/><path d="M-8 0 H8 M0 -8 V8" stroke="#6a6196" stroke-width="1.6"/></g></g>' for cx in (36, 134)))
    s.css.append("@keyframes whl{to{transform:rotate(360deg)}}")
    defs += '<filter id="blurR" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="6"/></filter>'
    # detection brackets that follow the car
    bw_, bh_ = 190, 96
    br = ""
    for (cx_, cy_, dx, dy) in [(-10, -84, 1, 1), (-10 + bw_, -84, -1, 1), (-10, -84 + bh_, 1, -1), (-10 + bw_, -84 + bh_, -1, -1)]:
        br += f'<path d="M{cx_ + dx * 16} {cy_} H{cx_} V{cy_ + dy * 16}" fill="none" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
    boxk = s.g(br, [(0, dict(stroke=GREEN, o=0)), (1.4, dict(stroke=GREEN, o=0)), (1.7, dict(stroke=GREEN, o=1)), (2.7, dict(stroke=GREEN)), (2.9, dict(stroke=AMBER)), (4.3, dict(stroke=AMBER)), (4.5, dict(stroke=RED)),
                         (6.2, dict(stroke=RED)), (6.4, dict(stroke=AMBER)), (6.9, dict(stroke=AMBER)), (7.1, dict(stroke=GREEN)), (7.6, dict(stroke=GREEN, o=1)), (7.9, dict(stroke=GREEN, o=0)), (D, dict(stroke=GREEN, o=0))])
    b.append('<g clip-path="url(#scn)">' + s.g(f'<g transform="translate(0,282)">{car}{boxk}</g>', [(t, dict(x=x)) for t, x in car_keys], ease="linear") + '</g>')

    # ---- rider ----
    rider = f'''
<path d="M-132 140 C-132 96 -84 70 -34 62 L52 62 C94 70 126 94 134 140Z" fill="url(#jacket)" stroke="{LINE}"/>
<path d="M-40 62 Q10 96 56 62" fill="none" stroke="{P1}" stroke-width="2.4" opacity=".7"/>
<path d="M-26 52 L-26 66 Q8 84 44 66 L44 52Z" fill="#241c48"/>
<path d="M-62 8 C-70 -52 -26 -92 24 -92 C74 -92 100 -54 100 -12 L100 28 C100 46 88 58 70 58 L-24 58 C-50 58 -60 40 -62 8Z" fill="url(#shell)" stroke="#5b4aa8" stroke-width="1.6"/>
<path d="M-58 -10 C-52 -58 -14 -84 24 -84" fill="none" stroke="#fff" stroke-width="2" opacity=".12"/>
<path d="M-60 14 C-40 6 20 8 98 22" fill="none" stroke="{P1}" stroke-width="3" opacity=".8"/>
<path d="M22 -34 C52 -46 90 -36 100 -12 L100 20 L18 20 C10 6 8 -18 22 -34Z" fill="url(#glass)" stroke="#0b0916" stroke-width="1.6"/>
<path d="M34 -30 C54 -36 74 -32 86 -22 L80 -22 C68 -28 52 -30 38 -26Z" fill="#fff" opacity=".18"/>
<rect x="-34" y="-12" width="36" height="24" rx="5" fill="#0f1f1b" stroke="#2f6b57" stroke-width="1.2"/><rect x="-27" y="-6" width="12" height="12" rx="2" fill="#0a0716" stroke="#3b3a63"/><path d="M-10 -6 H-1 M-10 0 H-1 M-10 6 H-3" stroke="#2f6b57" stroke-width="1.2"/>
<circle cx="76" cy="-64" r="9" fill="#0a0716" stroke="#6a6196" stroke-width="1.6"/><circle cx="76" cy="-64" r="4.6" fill="#201845"/><circle cx="74.5" cy="-65.5" r="1.5" fill="#fff" opacity=".7"/>
<rect x="84" y="30" width="20" height="20" rx="6" fill="#0f0c1c" stroke="#6a6196" stroke-width="1.3"/><circle cx="94" cy="40" r="6.4" fill="#1b1730" stroke="#3b3a63"/>
<g fill="#6a6196"><circle cx="92" cy="38" r=".9"/><circle cx="96" cy="38" r=".9"/><circle cx="94" cy="41" r=".9"/><circle cx="92" cy="43" r=".9"/><circle cx="96" cy="43" r=".9"/></g>'''
    b.append(at(470, 172, rider))
    # status LED on the visor + alcohol-sensor ripple
    b.append(s.el("circle", 'cx="504" cy="146" r="4.4"', [(0, dict(fill=GREEN)), (2.8, dict(fill=GREEN)), (2.9, dict(fill=AMBER)), (4.4, dict(fill=AMBER)), (4.5, dict(fill=RED)), (6.3, dict(fill=RED)), (6.4, dict(fill=AMBER)), (7.0, dict(fill=AMBER)), (7.1, dict(fill=GREEN)), (D, dict(fill=GREEN))]))
    for t0 in (1.0, 4.0, 7.0):
        b.append(at(564, 212, s.g(f'<circle r="10" fill="none" stroke="{GREEN}" stroke-width="1.6"/>', [(0, dict(o=0, s=.6)), (t0, dict(o=0, s=.6)), (t0 + .08, dict(o=.9, s=.7)), (t0 + 1.2, dict(o=0, s=2.6)), (D, dict(o=0, s=2.6))])))

    # ---- HUD ----
    b.append(f'<rect x="48" y="74" width="290" height="222" rx="18" fill="{SURF}" stroke="{LINE}"/>')
    b.append(T(68, 98, "helmet hud", 11.5, MUT, 600, "start"))
    b.append(s.el("circle", 'cx="318" cy="94" r="3.4"', [(0, dict(fill=GREEN)), (1.0, dict(fill="#1f3a2b")), (2.0, dict(fill=GREEN)), (3.0, dict(fill="#1f3a2b")), (4.0, dict(fill=GREEN)), (5.0, dict(fill="#1f3a2b")), (6.0, dict(fill=GREEN)), (7.0, dict(fill="#1f3a2b")), (8.0, dict(fill=GREEN)), (D, dict(fill=GREEN))]))
    def status(label, col, wins, flash=False):
        inner = (f'<rect x="68" y="108" width="250" height="56" rx="16" fill="{col}" fill-opacity=".13" stroke="{col}" stroke-width="1.8"/>'
                 f'<circle cx="96" cy="136" r="7.5" fill="{col}"/>' + T(122, 146, label, 24, col, 800, "start", extra=' letter-spacing="1.5"'))
        if flash:
            inner = s.g(inner, [(0, dict(o=1)), (.25, dict(o=.55)), (.5, dict(o=1))], ) .replace(f'{s.n}s infinite', '0.5s infinite') if False else inner
        st = []
        for (t0, t1) in wins:
            st += [(t0 - .001, dict(o=0)), (t0 + .12, dict(o=1)), (t1, dict(o=1)), (t1 + .12, dict(o=0))]
        st = sorted(st)
        return s.g(inner, [(0, dict(o=0))] + st + [(D, dict(o=0))] if wins[0][0] > .2 else st + [(D, dict(o=1 if wins[-1][1] >= D else 0))])
    b.append(status("SAFE", GREEN, [(0.3, 2.8), (7.0, D - .13)]) if False else "")
    # explicit layers so loop boundaries stay clean
    def layer(label, col, steps, pulse=False):
        inner = (f'<rect x="68" y="108" width="250" height="56" rx="16" fill="{col}" fill-opacity=".13" stroke="{col}" stroke-width="1.8"/>'
                 f'<circle cx="96" cy="136" r="7.5" fill="{col}"/>' + T(122, 146, label, 24, col, 800, "start", extra=' letter-spacing="1.5"'))
        if pulse:
            fl = s.kf([(0, dict(o=1)), (.25, dict(o=.55)), (.5, dict(o=1))])
            s.css.append(f".{fl}{{animation-duration:.5s}}")
            inner = f'<g class="{fl}">{inner}</g>'
        return s.g(inner, steps)
    b.append(layer("SAFE", GREEN, [(0, dict(o=1)), (2.7, dict(o=1)), (2.9, dict(o=0)), (6.9, dict(o=0)), (7.1, dict(o=1)), (D, dict(o=1))]))
    b.append(layer("WARNING", AMBER, [(0, dict(o=0)), (2.7, dict(o=0)), (2.9, dict(o=1)), (4.3, dict(o=1)), (4.5, dict(o=0)), (6.2, dict(o=0)), (6.4, dict(o=1)), (6.9, dict(o=1)), (7.1, dict(o=0)), (D, dict(o=0))]))
    b.append(layer("DANGER", RED, [(0, dict(o=0)), (4.3, dict(o=0)), (4.5, dict(o=1)), (6.2, dict(o=1)), (6.4, dict(o=0)), (D, dict(o=0))], pulse=True))
    # proximity bar
    b.append(T(68, 188, "proximity", 11.5, MUT, 600, "start"))
    b.append(f'<rect x="68" y="196" width="100" height="10" rx="5" fill="{GREEN}" opacity=".85"/><rect x="172" y="196" width="80" height="10" fill="{AMBER}" opacity=".9"/><rect x="256" y="196" width="62" height="10" rx="5" fill="{RED}" opacity=".9"/>')
    def bar_x(x):
        if x >= 889:
            f = max(0, (1215 - x) / (1215 - 889)) * .40
        elif x >= 720:
            f = .40 + (889 - x) / (889 - 720) * .32
        else:
            f = .72 + (720 - x) / (720 - 688) * .28
        return 68 + 250 * min(1, f)
    mk = [(t, dict(x=bar_x(x))) for t, x in car_keys]
    mk = [(t, dict(x=(68 if x >= 1190 else v["x"]))) for (t, v), (_, x) in zip(mk, car_keys)]
    b.append(s.g(f'<rect x="-2.5" y="190" width="5" height="22" rx="2.5" fill="#fff"/><circle cx="0" cy="190" r="3.6" fill="#fff"/>', mk, ease="linear"))
    # alcohol sensor card
    b.append(f'<rect x="68" y="224" width="250" height="56" rx="14" fill="#0f0c1c" stroke="{LINE}"/>')
    b.append(f'<circle cx="94" cy="252" r="13" fill="#1b1730" stroke="#6a6196"/><circle cx="94" cy="252" r="8" fill="#0f0c1c" stroke="#3b3a63"/><g fill="#6a6196"><circle cx="91" cy="249.5" r="1"/><circle cx="97" cy="249.5" r="1"/><circle cx="94" cy="253" r="1"/><circle cx="91" cy="256" r="1"/><circle cx="97" cy="256" r="1"/></g>')
    b.append(T(120, 244, "alcohol", 11.5, MUT, 600, "start") + T(120, 270, "0.00%", 22, TXT, 700, "start", fam=MONO))
    b.append(s.el("circle", 'cx="290" cy="252" r="4"', [(0, dict(fill=GREEN)), (.5, dict(fill="#1f3a2b")), (1.0, dict(fill=GREEN)), (1.5, dict(fill="#1f3a2b")), (2.0, dict(fill=GREEN)), (2.5, dict(fill="#1f3a2b")), (3.0, dict(fill=GREEN)), (3.5, dict(fill="#1f3a2b")), (4.0, dict(fill=GREEN)), (4.5, dict(fill="#1f3a2b")), (5.0, dict(fill=GREEN)), (5.5, dict(fill="#1f3a2b")), (6.0, dict(fill=GREEN)), (6.5, dict(fill="#1f3a2b")), (7.0, dict(fill=GREEN)), (7.5, dict(fill="#1f3a2b")), (8.0, dict(fill=GREEN)), (8.5, dict(fill="#1f3a2b")), (D, dict(fill=GREEN))], ease="linear"))
    b.append(T(300, 256, "ok", 12, GREEN, 700, "start"))
    save("smart_helmet_anim.svg", "Smart Helmet", "".join(b), s, defs)



# =====================================================================================
# 6. IoT BUS DETECTION, camera feed -> plate lock -> OCR -> bus details
# =====================================================================================
def bus():
    import random
    D = 9.0
    s = Scene(D)
    rnd = random.Random(7)
    FX, FY, FW, FH = 40, 70, 720, 228
    CX, GROUND = 400, 292
    PLATE = "KL 07 AX 4521"
    defs = f'''
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#150f33"/><stop offset="1" stop-color="#4a2a86"/></linearGradient>
<linearGradient id="rd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#241c42"/><stop offset="1" stop-color="#0d0919"/></linearGradient>
<linearGradient id="bbody" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6c52d6"/><stop offset=".5" stop-color="#4a3a9c"/><stop offset="1" stop-color="#2a2060"/></linearGradient>
<linearGradient id="bglass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0f22"/><stop offset="1" stop-color="#2c3770"/></linearGradient>
<radialGradient id="lampg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffd98a" stop-opacity=".55"/><stop offset="1" stop-color="#ffd98a" stop-opacity="0"/></radialGradient>
<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>
<radialGradient id="hglow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff6cf" stop-opacity=".5"/><stop offset="1" stop-color="#fff6cf" stop-opacity="0"/></radialGradient>
<clipPath id="feed"><rect x="{FX}" y="{FY}" width="{FW}" height="{FH}" rx="16"/></clipPath>'''
    b = []
    # ---- camera feed scene ----
    sc = [f'<rect x="{FX}" y="{FY}" width="{FW}" height="{FH}" fill="url(#sky)"/>']
    x = FX
    while x < FX + FW:
        w = rnd.randint(26, 54); h = rnd.randint(22, 78)
        sc.append(f'<rect x="{x}" y="{190 - h}" width="{w}" height="{h}" fill="#181038" opacity=".95"/>')
        for _ in range(rnd.randint(2, 6)):
            wx, wy = x + rnd.randint(4, max(5, w - 8)), 190 - h + rnd.randint(4, max(5, h - 8))
            sc.append(f'<rect x="{wx}" y="{wy}" width="4" height="5" fill="#ffd98a" opacity="{rnd.choice([.25, .5, .8])}"/>')
        x += w + rnd.randint(0, 4)
    sc.append(f'<rect x="{FX}" y="190" width="{FW}" height="{FH - 120}" fill="#120c27"/>')
    sc.append('<polygon points="332,190 468,190 700,298 100,298" fill="url(#rd)"/>')
    sc.append('<path d="M332 190 L100 298 M468 190 L700 298" stroke="#3b2f6e" stroke-width="2" fill="none"/>')
    for (y, h, w) in [(196, 4, 2), (206, 6, 3), (220, 10, 4), (240, 15, 6), (268, 22, 8)]:
        sc.append(f'<rect x="{CX - w / 2}" y="{y}" width="{w}" height="{h}" fill="#6a5cc8" opacity=".55"/>')
    for lx in (96, 704):
        sc.append(f'<circle cx="{lx}" cy="132" r="34" fill="url(#lampg)"/><rect x="{lx - 2}" y="132" width="4" height="150" fill="#1f1844"/><rect x="{lx - 10 if lx < 400 else lx - 4}" y="130" width="14" height="4" rx="2" fill="#2a2160"/><circle cx="{lx + (4 if lx < 400 else -2)}" cy="136" r="3.4" fill="#ffe6a8"/>')
    b.append(f'<g clip-path="url(#feed)">{"".join(sc)}')

    # ---- the bus (front view, origin = bottom centre) ----
    glass = (f'<rect x="-112" y="-140" width="224" height="84" rx="12" fill="url(#bglass)" stroke="#0b0916" stroke-width="2"/>'
             f'<path d="M-96 -136 L-40 -136 L-74 -60 L-100 -60Z M-20 -136 L8 -136 L-26 -60 L-54 -60Z" fill="#fff" opacity=".07"/>'
             f'<rect x="-1.5" y="-140" width="3" height="84" fill="#0b0916"/>'
             f'<circle cx="-58" cy="-104" r="10" fill="#0b0916" opacity=".85"/><path d="M-80 -58 Q-78 -88 -58 -90 Q-38 -88 -36 -58Z" fill="#0b0916" opacity=".85"/><ellipse cx="-58" cy="-78" rx="19" ry="5" fill="none" stroke="#3a3f7a" stroke-width="2"/>'
             f'<path d="M-100 -62 L-6 -92 M2 -62 L96 -92" stroke="#cfc8e8" stroke-width="1.6" opacity=".45"/>')
    plate = (f'<rect x="-46" y="-36" width="92" height="26" rx="4" fill="#f6f2e8" stroke="#2a2340" stroke-width="2"/><rect x="-42" y="-32" width="84" height="18" rx="2" fill="none" stroke="#1d1830" stroke-width=".8" opacity=".5"/>'
             + T(0, -17, PLATE, 13.5, "#14101f", 800, fam=MONO))
    busart = (f'<ellipse cx="0" cy="-2" rx="170" ry="16" fill="url(#hglow)"/>'
              f'<rect x="-136" y="-34" width="26" height="34" rx="6" fill="#0a0716"/><rect x="110" y="-34" width="26" height="34" rx="6" fill="#0a0716"/>'
              f'<rect x="-146" y="-124" width="14" height="34" rx="5" fill="#241c52"/><rect x="132" y="-124" width="14" height="34" rx="5" fill="#241c52"/>'
              f'<rect x="-130" y="-188" width="260" height="172" rx="20" fill="url(#bbody)" stroke="#1a1240" stroke-width="2"/>'
              f'<rect x="-52" y="-198" width="104" height="12" rx="5" fill="#2c2266"/><rect x="-126" y="-186" width="252" height="6" rx="3" fill="#fff" opacity=".12"/>'
              f'<rect x="-92" y="-176" width="184" height="30" rx="6" fill="#0a0716" stroke="#3a3158" stroke-width="1.4"/>'
              + T(0, -154.5, "117A  ALUVA", 17, AMBER, 800, fam=MONO, extra=' letter-spacing="1"') + glass +
              f'<rect x="-62" y="-52" width="124" height="22" rx="6" fill="#120f2c" stroke="#2a2160"/><path d="M-54 -46 H54 M-54 -41 H54 M-54 -36 H54" stroke="#2a2160" stroke-width="1.4"/>'
              f'<rect x="-122" y="-54" width="36" height="22" rx="8" fill="#fff6cf"/><rect x="86" y="-54" width="36" height="22" rx="8" fill="#fff6cf"/>'
              f'<rect x="-128" y="-32" width="256" height="18" rx="8" fill="#17122f" stroke="#2a2160"/>' + plate)
    box = ""
    for (cx_, cy_, dx, dy) in [(-142, -208, 1, 1), (142, -208, -1, 1), (-142, 4, 1, -1), (142, 4, -1, -1)]:
        box += f'<path d="M{cx_ + dx * 26} {cy_} H{cx_} V{cy_ + dy * 26}" fill="none" stroke="{P3}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
    boxg = s.g(box, [(0, dict(o=0)), (1.9, dict(o=0)), (2.2, dict(o=1)), (3.2, dict(o=1)), (3.5, dict(o=0)), (D, dict(o=0))])
    bus_in = s.g(busart + boxg,
                 [(0, dict(x=-8, y=-78, s=.3, o=0)), (.55, dict(x=-8, y=-78, s=.3, o=0)), (.8, dict(x=-8, y=-78, s=.3, o=1, e="cubic-bezier(.3,.1,.5,1)")), (2.9, dict(x=0, y=0, s=1, o=1)),
                  (6.9, dict(x=0, y=0, s=1, o=1)), (7.7, dict(x=0, y=24, s=1.45, o=0, e="cubic-bezier(.5,0,.8,.5)")), (D, dict(x=-8, y=-78, s=.3, o=0))])
    b.append(f'<g transform="translate({CX},{GROUND})">{bus_in}</g>')
    # vignette + feed chrome
    b.append(f'<rect x="{FX}" y="{FY}" width="{FW}" height="{FH}" fill="url(#vig)"/>')
    b.append('</g>')
    b.append(f'<rect x="{FX}" y="{FY}" width="{FW}" height="{FH}" rx="16" fill="none" stroke="{LINE}" stroke-width="1.6"/>')
    for (x_, y_, dx, dy) in [(FX + 14, FY + 14, 1, 1), (FX + FW - 14, FY + 14, -1, 1), (FX + 14, FY + FH - 14, 1, -1), (FX + FW - 14, FY + FH - 14, -1, -1)]:
        b.append(f'<path d="M{x_ + dx * 18} {y_} H{x_} V{y_ + dy * 18}" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="2" stroke-linecap="round"/>')
    b.append(s.el("circle", f'cx="{FX + 34}" cy="{FY + 30}" r="4.5"', [(0, dict(fill=RED)), (.5, dict(fill="#5a1f2c")), (1.0, dict(fill=RED)), (1.5, dict(fill="#5a1f2c")), (2.0, dict(fill=RED)), (2.5, dict(fill="#5a1f2c")), (3.0, dict(fill=RED)), (3.5, dict(fill="#5a1f2c")), (4.0, dict(fill=RED)), (4.5, dict(fill="#5a1f2c")), (5.0, dict(fill=RED)), (5.5, dict(fill="#5a1f2c")), (6.0, dict(fill=RED)), (6.5, dict(fill="#5a1f2c")), (7.0, dict(fill=RED)), (7.5, dict(fill="#5a1f2c")), (8.0, dict(fill=RED)), (8.5, dict(fill="#5a1f2c")), (D, dict(fill=RED))], ease="linear"))
    b.append(T(FX + 46, FY + 34, "REC", 11.5, "#e9e4f8", 700, "start") + T(FX + FW - 34, FY + 34, "CAM 01", 11.5, "#e9e4f8", 700, "end"))

    # ---- plate lock, OCR, extracted text (screen space, final bus position) ----
    b.append('<g clip-path="url(#feed)">')
    PX, PY = CX, GROUND - 23
    pb = ""
    for (dx, dy) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        cx_, cy_ = dx * 58, dy * 21
        pb += f'<path d="M{cx_ - dx * 14} {cy_} H{cx_} V{cy_ - dy * 10}" fill="none" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
    pbox = s.g(pb, [(0, dict(o=0, s=2.4, stroke=P3)), (3.2, dict(o=0, s=2.4, stroke=P3)), (3.45, dict(o=1, s=2.4, stroke=P3)), (3.9, dict(o=1, s=.94, stroke=P3)), (4.05, dict(o=1, s=1, stroke=P3)),
                         (4.8, dict(o=1, s=1, stroke=P3)), (4.95, dict(o=1, s=1.05, stroke=GREEN)), (5.1, dict(o=1, s=1, stroke=GREEN)), (6.7, dict(o=1, s=1, stroke=GREEN)), (6.95, dict(o=0, s=1, stroke=GREEN)), (D, dict(o=0, s=2.4, stroke=P3))])
    b.append(at(PX, PY, pbox))
    scan = f'<rect x="-2" y="-26" width="3" height="52" rx="1.5" fill="{P3}"/><rect x="-26" y="-26" width="26" height="52" fill="{P1}" opacity=".35"/>'
    b.append(at(PX, PY, s.g(scan, [(0, dict(o=0, x=-46)), (4.0, dict(o=0, x=-46)), (4.1, dict(o=1, x=-46)), (4.85, dict(o=1, x=48)), (4.95, dict(o=0, x=48)), (D, dict(o=0, x=-46))], ease="linear")))
    lab = f'<rect x="0" y="-11" width="86" height="22" rx="11" fill="{SURF2}" stroke="{P1}"/>' + T(43, 4, "plate 0.97", 11.5, TXT, 600)
    b.append(at(PX + 70, PY - 2, s.g(lab, [(0, dict(o=0)), (3.9, dict(o=0)), (4.1, dict(o=1)), (4.8, dict(o=1)), (5.0, dict(o=0)), (D, dict(o=0))])))
    chip = (f'<rect x="-92" y="-15" width="184" height="30" rx="15" fill="#0d0a1a" stroke="{GREEN}" stroke-width="1.6"/>'
            + T(0, 5.5, PLATE, 15, TXT, 800, fam=MONO) + f'<g class="{s.kf([(0, dict(sx=1)), (4.95, dict(sx=1)), (5.55, dict(sx=0)), (D, dict(sx=0))])}" style="transform-origin:90px 0">'
            f'<rect x="-88" y="-12" width="178" height="24" fill="#0d0a1a"/></g>')
    b.append(at(PX, PY - 38, s.g(chip, [(0, dict(o=0, y=6)), (4.85, dict(o=0, y=6)), (5.0, dict(o=1, y=0)), (6.7, dict(o=1, y=0)), (6.95, dict(o=0, y=0)), (D, dict(o=0, y=6))])))

    b.append('</g>')
    # idle panel (waiting for a bus) sits under the data panel
    qx = 784
    sk = [f'<rect x="{qx}" y="70" width="296" height="228" rx="18" fill="{SURF}" fill-opacity=".55" stroke="{LINE}" stroke-dasharray="4 6"/>',
          s.el("circle", f'cx="{qx + 34}" cy="104" r="5"', [(0, dict(fill=P1)), (.9, dict(fill="#2a2340")), (1.8, dict(fill=P1)), (2.7, dict(fill="#2a2340")), (3.6, dict(fill=P1)), (4.5, dict(fill="#2a2340")), (5.4, dict(fill=P1)), (D, dict(fill=P1))]),
          T(qx + 52, 109, "waiting for a bus\u2026", 14, MUT, 600, "start")]
    for i, (y, w1) in enumerate([(146, 150), (200, 90), (248, 170)]):
        sk.append(f'<rect x="{qx + 28}" y="{y}" width="70" height="8" rx="4" fill="#241d3f"/><rect x="{qx + 28}" y="{y + 20}" width="{w1}" height="14" rx="7" fill="#1d1832"/>')
    b.append("".join(sk))
    # ---- info panel ----
    pn = [f'<rect x="{qx}" y="70" width="296" height="228" rx="18" fill="{SURF}" stroke="{LINE}"/>',
          f'<circle cx="{qx + 34}" cy="104" r="14" fill="{GREEN}" fill-opacity=".16" stroke="{GREEN}" stroke-width="1.6"/><path d="M{qx + 27.5} 104.5 l4.8 4.8 l9 -10" stroke="{GREEN}" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
          T(qx + 58, 109, "Bus identified", 16, TXT, 700, "start"), f'<path d="M{qx + 24} 128 H{qx + 272}" stroke="{LINE}"/>']
    rows = [(142, "bus number", PLATE, 21, MONO), (196, "route", "117A", 21, MONO), (196, "", "", 0, None), (246, "destination", "Ernakulam \u2192 Aluva", 18, None)]
    def row(y, label, val, size, fam, delay, extra=""):
        r = T(qx + 28, y, label, 11.5, MUT, 600, "start") + T(qx + 28, y + 26, val, size, TXT, 800 if fam else 700, "start", fam=fam)
        return s.g(r + extra, [(0, dict(o=0, y=10)), (5.7 + delay, dict(o=0, y=10)), (6.0 + delay, dict(o=1, y=0)), (7.55, dict(o=1, y=0)), (7.9, dict(o=0, y=0)), (D, dict(o=0, y=10))])
    pn.append(row(150, "bus number", PLATE, 22, MONO, 0))
    pn.append(row(204, "route", "117A", 22, MONO, .15, f'<rect x="{qx + 100}" y="{204 + 7}" width="66" height="22" rx="11" fill="{P2}" fill-opacity=".25" stroke="{P1}"/>' + T(qx + 133, 204 + 22, "Express", 11.5, P3, 700)))
    pn.append(row(252, "destination", "Ernakulam \u2192 Aluva", 18, None, .3))
    b.append(s.g("".join(pn), [(0, dict(o=0, x=400)), (5.4, dict(o=0, x=400)), (5.55, dict(o=1, x=380)), (6.15, dict(o=1, x=0, e="cubic-bezier(.2,.8,.2,1)")), (7.4, dict(o=1, x=0)), (8.1, dict(o=0, x=400)), (D, dict(o=0, x=400))]))
    # data link from the feed to the panel
    b.append(f'<path d="M{FX + FW} 220 H{qx}" stroke="{P1}" stroke-width="2" stroke-dasharray="3 6" fill="none" class="{s.kf([(0, dict(o=0)), (5.2, dict(o=0)), (5.4, dict(o=.9)), (6.1, dict(o=.9)), (6.3, dict(o=0)), (D, dict(o=0))])}"/>')
    b.append(at(FX + FW, 220, s.g(f'<circle r="4.5" fill="{P3}"/>', [(0, dict(o=0, x=0)), (5.2, dict(o=0, x=0)), (5.3, dict(o=1, x=0)), (5.9, dict(o=1, x=36)), (6.0, dict(o=0, x=36)), (D, dict(o=0, x=0))], ease="linear")))
    save("bus_detection_anim.svg", "Real-Time IoT Bus Detection", "".join(b), s, defs)


if __name__ == "__main__":
    aura()
    prepper()
    prosthetic()
    songs()
    helmet()
    bus()
    print("All six SVGs generated in assets/")
