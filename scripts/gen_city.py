"""Builds assets/city.svg: an isometric 'contribution city' from a public GitHub profile.
No token needed. Taller tower = more contributions that day. stdlib only."""
import os, re, sys, urllib.request

USER = os.environ.get("GH_USER", "kewkatoo")
OUT = os.environ.get("CITY_OUT", "assets/city.svg")

BG, LINE, MUT, CREAM = "#0c0a13", "#2a2340", "#8b86a0", "#f5efe3"
PALETTE = {  # level: (top, left face, front face)
    0: ("#1c1932", "#14111f", "#0f0c18"),
    1: ("#7a5af0", "#5a3fc4", "#45309b"),
    2: ("#9373ff", "#6d4fe0", "#5238b0"),
    3: ("#b39dff", "#8366f0", "#6849cc"),
    4: ("#e4dbff", "#a58cf8", "#8268e0"),
}
UX, UY = 13.0, -4.6   # one week (column) step
VX, VY = 7.2, 5.2     # one weekday (row) step
MAXH = 74


def fetch():
    req = urllib.request.Request(
        f"https://github.com/users/{USER}/contributions",
        headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def attr(tag, name):
    m = re.search(r'(?<![-\w])' + name + r'="([^"]*)"', tag)
    return m.group(1) if m else None


def parse(html):
    tips = {}
    for m in re.finditer(r'<tool-tip[^>]*?\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        n = re.match(r'\s*(\d+)\s+contribution', m.group(2))
        tips[m.group(1)] = int(n.group(1)) if n else 0
    cells = []
    for m in re.finditer(r'<td\b[^>]*ContributionCalendar-day[^>]*>', html):
        tag = m.group(0)
        cid, date, level = attr(tag, "id"), attr(tag, "data-date"), attr(tag, "data-level")
        mm = re.search(r'-(\d+)-(\d+)$', cid or "")
        if not (mm and date):
            continue
        r, c = int(mm.group(1)), int(mm.group(2))
        lvl = int(level or 0)
        cnt = tips.get(cid, [0, 1, 3, 6, 10][min(lvl, 4)])
        cells.append(dict(r=r, c=c, date=date, level=min(lvl, 4), n=cnt))
    return cells


def P(c, r):
    return (c * UX + r * VX, c * UY + r * VY)


def pts(*p):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in p)


def streaks(cells):
    days = sorted(cells, key=lambda d: d["date"])
    best = cur = 0
    for d in days:
        cur = cur + 1 if d["n"] > 0 else 0
        best = max(best, cur)
    # current streak: allow today to still be empty
    run, seq = 0, days[::-1]
    for i, d in enumerate(seq):
        if d["n"] > 0:
            run += 1
        elif i == 0:
            continue
        else:
            break
    return best, run


def build(cells):
    maxc = max([d["n"] for d in cells] + [1])
    total = sum(d["n"] for d in cells)
    active = sum(1 for d in cells if d["n"] > 0)
    best, now = streaks(cells)
    latest = max(cells, key=lambda d: d["date"])

    def height(n):
        return 2.5 if n == 0 else 4 + MAXH * (n / maxc) ** 0.55

    # bounds
    xs, ys = [], []
    for d in cells:
        h = height(d["n"])
        for (cc, rr) in ((d["c"], d["r"]), (d["c"] + 1, d["r"] + 1), (d["c"] + 1, d["r"]), (d["c"], d["r"] + 1)):
            x, y = P(cc, rr)
            xs.append(x); ys.append(y - h); ys.append(y)
    W = 900
    H = int(max(ys) - min(ys) + 40 + 56)
    ox = (W - (max(xs) - min(xs))) / 2 - min(xs)
    oy = 40 - min(ys)

    def tile(d):
        c, r, h = d["c"], d["r"], height(d["n"])
        p0, p1, p2, p3 = P(c, r), P(c + 1, r), P(c + 1, r + 1), P(c, r + 1)
        sh = lambda p, k=0: (p[0] + ox, p[1] + oy - k)
        t, l, f = PALETTE[d["level"]]
        top = pts(sh(p0, h), sh(p1, h), sh(p2, h), sh(p3, h))
        left = pts(sh(p0), sh(p3), sh(p3, h), sh(p0, h))
        front = pts(sh(p3), sh(p2), sh(p2, h), sh(p3, h))
        body = (f'<polygon points="{left}" fill="{l}"/><polygon points="{front}" fill="{f}"/>'
                f'<polygon points="{top}" fill="{t}" stroke="{BG}" stroke-width=".4"/>')
        return body, sh(p3)

    flat = [d for d in cells if d["n"] == 0]
    tall = [d for d in cells if d["n"] > 0]
    out = []
    # back to front: far columns first, near rows last
    for d in sorted(flat, key=lambda d: (-d["c"], d["r"])):
        out.append(tile(d)[0])
    for d in sorted(tall, key=lambda d: (-d["c"], d["r"])):
        body, base = tile(d)
        delay = d["c"] * 0.018
        breathe = ""
        out.append(f'<g class="g" style="transform-origin:{base[0]:.1f}px {base[1]:.1f}px;'
                   f'animation-delay:{delay:.2f}s">{body}</g>')
    # beacon on latest day
    c, r, h = latest["c"], latest["r"], height(latest["n"])
    q = [P(c, r), P(c + 1, r), P(c + 1, r + 1), P(c, r + 1)]
    q = [(x + ox, y + oy - h) for x, y in q]
    out.append(f'<polygon class="beacon" points="{pts(*q)}" fill="none" stroke="{CREAM}" stroke-width="1.6"/>')

    legend = "".join(
        f'<rect x="{700 + i * 22}" y="{H - 38}" width="14" height="14" rx="3" fill="{PALETTE[i][0]}"/>'
        for i in range(5))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{total} contributions in the last year, shown as a 3D city">
<defs><radialGradient id="glow" cx="60%" cy="45%" r="60%"><stop offset="0" stop-color="#3b1f7a" stop-opacity=".45"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient></defs>
<style>
text{{font-family:Inter,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}}
.g{{animation:grow 1.1s cubic-bezier(.2,.8,.2,1) backwards}}
@keyframes grow{{from{{transform:scaleY(.02);opacity:0}}}}
.beacon{{animation:beacon 2.2s ease-in-out infinite}}
@keyframes beacon{{0%,100%{{opacity:.15}}50%{{opacity:1}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<rect width="{W}" height="{H}" rx="22" fill="{BG}"/>
<rect width="{W}" height="{H}" rx="22" fill="url(#glow)"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="{LINE}"/>
<text x="40" y="52" font-size="13" fill="{MUT}">daily progress</text>
<text x="40" y="100" font-size="46" font-weight="700" fill="{CREAM}">{total}</text>
<text x="40" y="124" font-size="13" fill="#b9b3cc">contributions in the last year</text>
<text x="40" y="156" font-size="13" fill="#a29cb8">{active} active days</text>
<text x="40" y="177" font-size="13" fill="#a29cb8">busiest day: {maxc}</text>
<text x="40" y="198" font-size="13" fill="#a29cb8">longest streak: {best} day{"s" if best != 1 else ""}</text>
{"".join(out)}
<text x="860" y="{H - 58}" text-anchor="end" font-size="12.5" fill="{MUT}">every tower is a day. taller means more commits.</text>
<text x="690" y="{H - 27}" text-anchor="end" font-size="12" fill="{MUT}">less</text>
{legend}
<text x="816" y="{H - 27}" font-size="12" fill="{MUT}">more</text>
</svg>'''
    return svg, total


if __name__ == "__main__":
    try:
        cells = parse(fetch())
        if len(cells) < 300:
            raise RuntimeError(f"only parsed {len(cells)} cells")
    except Exception as e:  # keep the previous city if GitHub is unreachable
        print("city not updated:", e)
        sys.exit(0)
    svg, total = build(cells)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(svg)
    print(f"wrote {OUT}: {total} contributions, {len(cells)} days")
