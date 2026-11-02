"""Composes assets/profile.svg: hero + 3D city + bio + six project tiles (2 columns) + footer
inside ONE container. Reads assets/hero.svg, assets/city.svg and the scenes from gen_projects.py.
Run from the repo root:  python scripts/gen_projects.py && python scripts/build_profile.py"""
import math, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import gen_projects as gp

W = 1200
BG, CARD, LINE, TXT, MUT, CREAM = gp.BG, gp.CARD, gp.LINE, gp.TXT, gp.MUT, gp.CREAM
P1, P2, P3 = gp.P1, gp.P2, gp.P3
SANS = gp.SANS


# ---------- helpers: make ids / class / keyframe names unique per embedded piece ----------
def ns_ids(prefix, *texts):
    joined = "\u0000".join(texts)
    for i in set(re.findall(r'\bid="([^"]+)"', joined)):
        joined = (joined.replace(f'id="{i}"', f'id="{prefix}-{i}"').replace(f'url(#{i})', f'url(#{prefix}-{i})')
                  .replace(f'href="#{i}"', f'href="#{prefix}-{i}"'))
    return joined.split("\u0000")


def ns_anim(prefix, css, body):
    css = re.sub(r'@media[^{]*\{\*\{[^}]*\}\}', '', css)
    css = re.sub(r'(^|\})\s*text\{[^}]*\}', r'\1', css)
    kfs = set(re.findall(r'@keyframes\s+([\w-]+)', css))
    cls = set(re.findall(r'\.([\w-]+)\s*\{', css))
    for n in sorted(kfs | cls, key=len, reverse=True):
        css = re.sub(rf'@keyframes\s+{re.escape(n)}\b', f'@keyframes {prefix}-{n}', css)
        css = re.sub(rf'\.{re.escape(n)}(\s*\{{)', rf'.{prefix}-{n}\1', css)
        css = re.sub(rf'animation:{re.escape(n)}(\s)', rf'animation:{prefix}-{n}\1', css)
        body = re.sub(rf'animation:{re.escape(n)}(\s)', rf'animation:{prefix}-{n}\1', body)
        body = re.sub(rf'class="{re.escape(n)}"', f'class="{prefix}-{n}"', body)
    return css, body


def split_svg(path):
    t = open(path, encoding="utf-8").read()
    w, h = [float(x) for x in re.search(r'width="([\d.]+)" height="([\d.]+)"', t).groups()]
    defs = re.search(r'<defs>(.*?)</defs>', t, re.S).group(1)
    css = re.search(r'<style>(.*?)</style>', t, re.S).group(1)
    body = t[t.index('</style>') + 8:t.rindex('</svg>')]
    body = re.sub(r'<rect[^>]*\brx="22"[^>]*/>', '', body)                      # drop own card background / border / glow
    body = re.sub(r'<g>(?:\s*<rect class="b"[^>]*/>)+\s*</g>', '', body)       # drop hero's own equalizer
    return w, h, defs, css, body


def piece(prefix, path):
    w, h, defs, css, body = split_svg(path)
    defs, body = ns_ids(prefix, defs, body)
    css, body = ns_anim(prefix, css, body)
    return w, h, defs, css, body


# ---------- composition ----------
def eq_row(x0, x1, base, maxh, seed, pitch=20):
    n = int((x1 - x0) / pitch)
    out = []
    for i in range(n):
        h = maxh * (.45 + .55 * abs(math.sin(i * .55 + seed) * math.cos(i * .17)))
        dur = 1.1 + ((i * 7 + seed) % 6) * .22
        dl = -((i * 13) % 10) * .23
        out.append(f'<rect class="eqb" x="{x0 + i * pitch + 3:.1f}" y="{base - h:.1f}" width="10" height="{h:.1f}" rx="2" style="animation-duration:{dur:.2f}s;animation-delay:{dl:.2f}s"/>')
    return "".join(out)


def build(out="assets/profile.svg"):
    gp.REG.clear()
    for fn in (gp.aura, gp.prepper, gp.prosthetic, gp.songs, gp.helmet, gp.bus):
        fn()
    defs, css, body = [], [], []

    hw, hh, d, c, bd = piece("hero", "assets/hero.svg"); defs.append(d); css.append(c)
    body.append(f'<g transform="translate({(W - hw) / 2:.0f},14)">{bd}</g>')
    y = 14 + 352
    body.append(f'<g>{eq_row(36, W - 36, y + 8, 34, 2)}</g>')
    y += 22

    cw, ch, d, c, bd = piece("city", "assets/city.svg"); defs.append(d); css.append(c)
    body.append(f'<g transform="translate({(W - cw) / 2:.0f},{y})">{bd}</g>')
    y += ch + 8

    for i, (t, col, sz) in enumerate([("electronics &amp; computer engineering graduate from amrita vishwa vidyapeetham.", "#d9d3ee", 15.5),
                                       ("i build complete ai systems, from data processing and inference to apis,", "#b9b3cc", 15.5),
                                       ("hardware integration and real-world interaction.", "#b9b3cc", 15.5)]):
        body.append(f'<text x="{W / 2}" y="{y + 20 + i * 25}" text-anchor="middle" font-size="{sz}" fill="{col}">{t}</text>')
    y += 96
    body.append(f'<path d="M{W / 2 - 150} {y} H{W / 2 - 74} M{W / 2 + 74} {y} H{W / 2 + 150}" stroke="{LINE}" stroke-width="1.4"/>'
                f'<text x="{W / 2}" y="{y + 4.5}" text-anchor="middle" font-size="12.5" letter-spacing="2.5" fill="{MUT}">selected work</text>')
    y += 28

    # ---- project tiles ----
    PADX, GAP, TH = 36, 20, 214
    TW = (W - 2 * PADX - GAP) / 2
    tiles = [("aura_anim.svg", (10, 960, 62, 306)), ("adaptive_learning_anim.svg", (110, 1090, 62, 306)),
             ("prosthetic_arm_anim.svg", (240, 960, 62, 306)), ("song_recommendation_anim.svg", (30, 1176, 62, 306)),
             ("smart_helmet_anim.svg", (20, 1010, 62, 306)), ("bus_detection_anim.svg", (20, 1100, 62, 306))]
    for i, (name, (x0, x1, y0, y1)) in enumerate(tiles):
        r = gp.REG[name]
        pre = f"p{i}"
        dd, bb = ns_ids(pre, r["defs"], r["body"])
        cc, bb = ns_anim(pre, r["css"], bb)
        defs.append(dd); css.append(cc)
        tx = PADX + (i % 2) * (TW + GAP)
        ty = y + (i // 2) * (TH + GAP)
        cx, cy, cwid, chei = tx + 12, ty + 40, TW - 24, TH - 52
        s = min(cwid / (x1 - x0), chei / (y1 - y0))
        ox = cx + (cwid - s * (x1 - x0)) / 2
        oy = cy + (chei - s * (y1 - y0)) / 2
        defs.append(f'<linearGradient id="tg{i}" gradientUnits="userSpaceOnUse" x1="{cx}" x2="{cx + cwid}" y1="0" y2="0"><stop offset="0" stop-color="#000"/><stop offset=".05" stop-color="#fff"/><stop offset=".95" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
                    f'<mask id="tm{i}" maskUnits="userSpaceOnUse" x="{cx}" y="{cy}" width="{cwid}" height="{chei}"><rect x="{cx}" y="{cy}" width="{cwid}" height="{chei}" fill="url(#tg{i})"/></mask>')
        body.append(f'<rect x="{tx}" y="{ty}" width="{TW}" height="{TH}" rx="18" fill="{CARD}" stroke="{LINE}"/>'
                    f'<text x="{tx + 20}" y="{ty + 29}" font-size="14" font-weight="650" fill="{TXT}">{r["title"]}</text>'
                    f'<g mask="url(#tm{i})"><svg x="{cx}" y="{cy}" width="{cwid}" height="{chei}">'
                    f'<g transform="translate({ox - cx - x0 * s:.2f},{oy - cy - y0 * s:.2f}) scale({s:.4f})">{bb}</g></svg></g>')
    y += 3 * TH + 2 * GAP + 30

    body.append(f'<text x="{W / 2}" y="{y + 6}" text-anchor="middle" font-size="13" fill="{MUT}">thanks for stopping by. stay curious, turn it up.</text>')
    body.append(f'<g>{eq_row(36, W - 36, y + 78, 44, 5)}</g>')
    H = y + 90

    css.append(f'text{{font-family:{SANS}}}.eqb{{fill:url(#eqg);transform-box:fill-box;transform-origin:50% 100%;animation:eqk ease-in-out infinite alternate}}'
               '@keyframes eqk{from{transform:scaleY(.22)}to{transform:scaleY(1)}}@media (prefers-reduced-motion:reduce){*{animation:none!important}}')
    head = (f'<defs><linearGradient id="bdr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7c5cff"/><stop offset=".5" stop-color="#5b3df5"/><stop offset="1" stop-color="#2b174f"/></linearGradient>'
            f'<linearGradient id="eqg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P3}" stop-opacity=".55"/><stop offset="1" stop-color="{P2}" stop-opacity=".12"/></linearGradient>'
            f'<radialGradient id="g1" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#3b1f7a" stop-opacity=".5"/><stop offset="1" stop-color="#3b1f7a" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="cont"><rect width="{W}" height="{H:.0f}" rx="30"/></clipPath>{"".join(defs)}</defs>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}" role="img" aria-label="Aditya Achary: AI engineer, data analyst and music producer. Projects: AURA, Prepper, Prosthetic Arm, Song Recommendation, Smart Helmet, IoT Bus Detection.">'
           f'{head}<style>{"".join(css)}</style>'
           f'<rect width="{W}" height="{H:.0f}" rx="30" fill="{BG}"/>'
           f'<g clip-path="url(#cont)"><ellipse cx="600" cy="190" rx="560" ry="230" fill="url(#g1)"/><ellipse cx="600" cy="{y - 380:.0f}" rx="560" ry="330" fill="url(#g1)" opacity=".5"/>{"".join(body)}</g>'
           f'<rect x="1" y="1" width="{W - 2}" height="{H - 2:.0f}" rx="29" fill="none" stroke="url(#bdr)" stroke-width="2"/></svg>')
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {out}: {W}x{H:.0f}, {len(svg) / 1024:.0f} KB")


if __name__ == "__main__":
    build()
