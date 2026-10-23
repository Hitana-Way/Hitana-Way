"""Draws the GitHub contribution calendar as a starry sky (night) or a sakura field (day)."""
import json
import os
import random
import sys
import urllib.request

W, H = 1200, 210
COLS, ROWS = 53, 7
X0, Y0, DX, DY = 34, 30, 21.6, 24

QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
weeks{contributionDays{contributionCount contributionLevel}}}}}}"""
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    weeks = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [[LEVELS[d["contributionLevel"]] for d in w["contributionDays"]] for w in weeks]


def fake():
    rnd = random.Random(1)
    return [[rnd.choice([0, 0, 0, 1, 1, 2, 3, 4]) for _ in range(7)] for _ in range(COLS)]


def cells(weeks):
    rnd = random.Random(42)
    weeks = weeks[-COLS:]
    for c, week in enumerate(weeks):
        for r, level in enumerate(week):
            x = X0 + c * DX + rnd.uniform(-5, 5)
            y = Y0 + r * DY + rnd.uniform(-5, 5)
            yield round(x, 1), round(y, 1), level, round(rnd.uniform(0, 4), 2)


def night(weeks):
    out = []
    for x, y, lv, delay in cells(weeks):
        if lv == 0:
            out.append(f'<circle cx="{x}" cy="{y}" r=".9" fill="#7b5fb0" opacity=".55"/>')
        elif lv <= 2:
            out.append(f'<circle class="tw" style="animation-delay:-{delay}s" cx="{x}" cy="{y}" r="{1.4 + lv * .6}" fill="#e9d8ff"/>')
        else:
            s = 4 + (lv - 3) * 2.5
            out.append(f'<use class="tw glow" style="animation-delay:-{delay}s" href="#spark" '
                       f'transform="translate({x} {y}) scale({s})" fill="{"#fff6fb" if lv == 4 else "#ffd6ef"}"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#140a2c"/><stop offset="1" stop-color="#22134a"/>
    </linearGradient>
    <path id="spark" d="M0 -1 Q0 0 1 0 Q0 0 0 1 Q0 0 -1 0 Q0 0 0 -1Z"/>
    <filter id="g" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      .tw{{animation:tw 3.5s ease-in-out infinite}}
      .glow{{filter:url(#g)}}
      @keyframes tw{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}
    </style>
  </defs>
  <rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>
  {"".join(out)}
</svg>
'''


def day(weeks):
    out = []
    for x, y, lv, delay in cells(weeks):
        if lv == 0:
            out.append(f'<circle cx="{x}" cy="{y}" r="1.6" fill="#c9b3ee"/>')
        else:
            s = .55 + lv * .3
            fill = ("#ffd6ea", "#ffb7d9", "#f497c6", "#c77dff")[lv - 1]
            out.append(f'<g transform="translate({x} {y}) scale({s})"><use class="sway" style="animation-delay:-{delay}s" href="#flower" fill="{fill}"/></g>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f3e8ff"/><stop offset="1" stop-color="#ffe4ef"/>
    </linearGradient>
    <g id="flower">
      <g>
        <ellipse cx="0" cy="-3.2" rx="2.4" ry="3.4"/>
        <ellipse cx="0" cy="-3.2" rx="2.4" ry="3.4" transform="rotate(72)"/>
        <ellipse cx="0" cy="-3.2" rx="2.4" ry="3.4" transform="rotate(144)"/>
        <ellipse cx="0" cy="-3.2" rx="2.4" ry="3.4" transform="rotate(216)"/>
        <ellipse cx="0" cy="-3.2" rx="2.4" ry="3.4" transform="rotate(288)"/>
      </g>
      <circle r="1.5" fill="#fff3c4"/>
    </g>
    <style>
      .sway{{animation:sw 4s ease-in-out infinite}}
      @keyframes sw{{0%,100%{{transform:rotate(-14deg)}}50%{{transform:rotate(14deg)}}}}
    </style>
  </defs>
  <rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>
  {"".join(out)}
</svg>
'''


if __name__ == "__main__":
    mode, out_path = sys.argv[1], sys.argv[2]
    token = os.environ.get("GITHUB_TOKEN")
    weeks = fetch(os.environ["GITHUB_USER"], token) if token else fake()
    with open(out_path, "w") as f:
        f.write((night if mode == "night" else day)(weeks))
