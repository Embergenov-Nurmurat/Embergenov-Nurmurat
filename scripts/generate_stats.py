#!/usr/bin/env python3
"""Generates terminal-styled GitHub stats cards (stats-light.svg / stats-dark.svg).

Uses only the standard library. Data comes from the GitHub GraphQL API.
Usage:
    GITHUB_TOKEN=... python scripts/generate_stats.py --user Embergenov-Nurmurat
    python scripts/generate_stats.py --demo      # offline preview with fake data
"""
import argparse
import json
import os
import urllib.request
from datetime import datetime, timezone
from html import escape

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    following { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100,
                 privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar { totalContributions }
    }
  }
}
"""

THEMES = {
    "light": dict(
        bg1="#FFFFFF", bg2="#F8FAFC", bg3="#EEF6FF",
        b1="#2563EB", b2="#06B6D4", b3="#7C3AED",
        title="#1D4ED8", text="#0F172A", muted="#475569",
        track="#CBD5E1", panel="#FFFFFF", panel_op=".75",
    ),
    "dark": dict(
        bg1="#030712", bg2="#07111F", bg3="#0B1220",
        b1="#7C3AED", b2="#22D3EE", b3="#10B981",
        title="#22D3EE", text="#F8FAFC", muted="#94A3B8",
        track="#334155", panel="#0F172A", panel_op=".55",
    ),
}

FALLBACK_COLORS = ["#3776AB", "#7F52FF", "#E34F26", "#1572B6", "#3DDC84", "#F59E0B"]


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise SystemExit(payload["errors"])
    u = payload["data"]["user"]
    langs = {}
    stars = 0
    for repo in u["repositories"]["nodes"]:
        stars += repo["stargazerCount"]
        for e in repo["languages"]["edges"]:
            n = e["node"]
            item = langs.setdefault(n["name"], [0, n["color"]])
            item[0] += e["size"]
    cc = u["contributionsCollection"]
    return dict(
        since=u["createdAt"][:4],
        followers=u["followers"]["totalCount"],
        following=u["following"]["totalCount"],
        repos=u["repositories"]["totalCount"],
        stars=stars,
        commits=cc["totalCommitContributions"],
        prs=cc["totalPullRequestContributions"],
        issues=cc["totalIssueContributions"],
        total=cc["contributionCalendar"]["totalContributions"],
        langs=sorted(langs.items(), key=lambda kv: -kv[1][0])[:5],
    )


def demo_data():
    return dict(
        since="2024", followers=12, following=8, repos=9, stars=5,
        commits=214, prs=6, issues=2, total=231,
        langs=[("Python", [52000, "#3572A5"]), ("HTML", [18000, "#e34c26"]),
               ("Kotlin", [9000, "#A97BFF"]), ("CSS", [6000, "#563d7c"])],
    )


def render(d, t, user):
    W, H = 1180, 366
    out = []
    a = out.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'role="img" aria-label="GitHub stats for {escape(user)}">')
    a('<style>text{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}'
      '.fade{opacity:0;animation:f .6s ease forwards}'
      '@keyframes f{to{opacity:1}}'
      '.bar{transform-origin:0 0;transform:scaleX(0);animation:g 1.1s cubic-bezier(.2,.8,.2,1) forwards}'
      '@keyframes g{to{transform:scaleX(1)}}'
      '.cur{animation:b 1.1s steps(1) infinite}@keyframes b{50%{opacity:0}}</style>')
    a(f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
      f'<stop offset="0" stop-color="{t["bg1"]}"/><stop offset=".55" stop-color="{t["bg2"]}"/>'
      f'<stop offset="1" stop-color="{t["bg3"]}"/></linearGradient>'
      f'<linearGradient id="bd" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="{H}">'
      f'<stop offset="0" stop-color="{t["b1"]}"/><stop offset=".5" stop-color="{t["b2"]}"/>'
      f'<stop offset="1" stop-color="{t["b3"]}"/></linearGradient>'
      f'<clipPath id="r"><rect x="24" y="24" width="{W-48}" height="{H-48}" rx="22"/></clipPath></defs>')
    a(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="30" fill="url(#bg)"/>')
    a(f'<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="30" fill="none" '
      f'stroke="url(#bd)" stroke-opacity=".55" stroke-width="1.5"/>')
    # window chrome
    for cx, col in ((46, "#EF4444"), (66, "#F59E0B"), (86, "#10B981")):
        a(f'<circle cx="{cx}" cy="42" r="6" fill="{col}"/>')
    a(f'<text x="108" y="46" font-size="13" fill="{t["muted"]}">'
      f'{escape(user.lower())}@profile:~$ ./stats.sh<tspan class="cur" fill="{t["title"]}"> ▌</tspan></text>')
    a(f'<text x="{W-46}" y="46" font-size="12" text-anchor="end" fill="{t["muted"]}">'
      f'updated {datetime.now(timezone.utc):%Y-%m-%d}</text>')
    a(f'<line x1="46" y1="62" x2="{W-46}" y2="62" stroke="{t["muted"]}" stroke-opacity=".25"/>')

    # left panel: metrics
    a(f'<text x="310" y="92" font-size="13" font-weight="700" letter-spacing="4" '
      f'text-anchor="middle" fill="{t["title"]}">STATS.LOG</text>')
    metrics = [
        ("REPOS", d["repos"]), ("STARS", d["stars"]),
        ("FOLLOWERS", d["followers"]), ("COMMITS / 1Y", d["commits"]),
        ("PULL REQUESTS", d["prs"]), ("ISSUES", d["issues"]),
    ]
    for i, (label, val) in enumerate(metrics):
        col, row = i % 2, i // 2
        x = 60 + col * 250
        y = 120 + row * 62
        a(f'<g class="fade" style="animation-delay:{.1 + i * .08:.2f}s">'
          f'<rect x="{x}" y="{y}" width="230" height="52" rx="12" fill="{t["panel"]}" '
          f'fill-opacity="{t["panel_op"]}" stroke="{t["track"]}"/>'
          f'<text x="{x+16}" y="{y+21}" font-size="10.5" letter-spacing="2" fill="{t["muted"]}">{label}</text>'
          f'<text x="{x+16}" y="{y+42}" font-size="20" font-weight="700" fill="{t["text"]}">{val:,}</text>'
          f'</g>')
    a(f'<text x="60" y="{H-34}" font-size="12" fill="{t["muted"]}">'
      f'{d["total"]:,} contributions in the last year · on GitHub since {d["since"]}</text>')

    # divider
    a(f'<line x1="600" y1="84" x2="600" y2="{H-48}" stroke="{t["muted"]}" stroke-opacity=".25"/>')

    # right panel: languages
    a(f'<text x="890" y="92" font-size="13" font-weight="700" letter-spacing="4" '
      f'text-anchor="middle" fill="{t["title"]}">TOP.LANGUAGES</text>')
    total = sum(v[0] for _, v in d["langs"]) or 1
    bx, bw = 640, 460
    for i, (name, (size, color)) in enumerate(d["langs"]):
        pct = size / total * 100
        y = 126 + i * 38
        color = color or FALLBACK_COLORS[i % len(FALLBACK_COLORS)]
        a(f'<g class="fade" style="animation-delay:{.2 + i * .1:.2f}s">'
          f'<circle cx="{bx+4}" cy="{y-4}" r="4" fill="{color}"/>'
          f'<text x="{bx+18}" y="{y}" font-size="13" fill="{t["text"]}">{escape(name)}</text>'
          f'<text x="{bx+bw}" y="{y}" font-size="13" text-anchor="end" fill="{t["muted"]}">{pct:.1f}%</text>'
          f'<rect x="{bx}" y="{y+8}" width="{bw}" height="6" rx="3" fill="{t["track"]}" fill-opacity=".6"/>'
          f'<rect class="bar" style="animation-delay:{.4 + i * .1:.2f}s" x="{bx}" y="{y+8}" '
          f'width="{max(pct / 100 * bw, 4):.1f}" height="6" rx="3" fill="{color}"/></g>')
    a('</svg>')
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--user", default=os.environ.get("GITHUB_ACTOR", "Embergenov-Nurmurat"))
    p.add_argument("--out", default=".")
    p.add_argument("--demo", action="store_true")
    args = p.parse_args()
    data = demo_data() if args.demo else fetch(args.user, os.environ["GITHUB_TOKEN"])
    os.makedirs(args.out, exist_ok=True)
    for name, theme in THEMES.items():
        path = os.path.join(args.out, f"stats-{name}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(render(data, theme, args.user))
        print("wrote", path)


if __name__ == "__main__":
    main()
