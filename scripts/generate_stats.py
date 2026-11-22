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
from datetime import datetime, timedelta, timezone
from html import escape
from datetime import date as _date
import festive

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
        name
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
    print(f"user: {login}")
    for repo in u["repositories"]["nodes"]:
        print(f"  repo {repo['name']}: {repo['stargazerCount']} stars")
    print(f"followers={u['followers']['totalCount']} repos={u['repositories']['totalCount']} "
          f"stars={stars} commits(1y)={cc['totalCommitContributions']} "
          f"prs={cc['totalPullRequestContributions']} issues={cc['totalIssueContributions']} "
          f"contributions={cc['contributionCalendar']['totalContributions']}")
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


def render(d, t, user, theme_name="light", festive_on=False):
    W = 560
    n_lang = max(len(d["langs"]), 1)
    lang_top = 394
    H = lang_top + (n_lang - 1) * 48 + 92
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
      f'<stop offset="1" stop-color="{t["b3"]}"/></linearGradient></defs>')
    a(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="28" fill="url(#bg)"/>')
    a(f'<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="28" fill="none" '
      f'stroke="url(#bd)" stroke-opacity=".6" stroke-width="1.5"/>')
    if festive_on:
        a(f'<style>{festive.css(H)}</style>')
        a(festive.snow(W, H, n=30, seed=5, **festive.snow_style(theme_name)))
        a(festive.garland(W, y0=5, sag=8, segs=5, margin=44, wire=t["muted"], bulb_r=3.6, hang=5))
    # window chrome
    for cx, col in ((36, "#EF4444"), (58, "#F59E0B"), (80, "#10B981")):
        a(f'<circle cx="{cx}" cy="40" r="7" fill="{col}"/>')
    a(f'<text x="102" y="45" font-size="14" fill="{t["muted"]}">'
      f'{escape(user.lower())}@profile:~$<tspan class="cur" fill="{t["title"]}"> ▌</tspan></text>')
    a(f'<line x1="32" y1="62" x2="{W-32}" y2="62" stroke="{t["muted"]}" stroke-opacity=".25"/>')

    # metrics: 3 columns x 2 rows
    a(f'<text x="{W/2}" y="98" font-size="15" font-weight="700" letter-spacing="5" '
      f'text-anchor="middle" fill="{t["title"]}">STATS.LOG</text>')
    metrics = [
        ("REPOS", d["repos"]), ("STARS", d["stars"]), ("FOLLOWERS", d["followers"]),
        ("COMMITS/1Y", d["commits"]), ("PULL REQ.", d["prs"]), ("ISSUES", d["issues"]),
    ]
    cw, gap, x0 = 156, 12, 32
    for i, (label, val) in enumerate(metrics):
        col, row = i % 3, i // 3
        x = x0 + col * (cw + gap)
        y = 120 + row * 92
        a(f'<g class="fade" style="animation-delay:{.1 + i * .08:.2f}s">'
          f'<rect x="{x}" y="{y}" width="{cw}" height="80" rx="14" fill="{t["panel"]}" '
          f'fill-opacity="{t["panel_op"]}" stroke="{t["track"]}"/>'
          f'<text x="{x+16}" y="{y+28}" font-size="12" letter-spacing="1.5" fill="{t["muted"]}">{label}</text>'
          f'<text x="{x+16}" y="{y+62}" font-size="30" font-weight="700" fill="{t["text"]}">{val:,}</text>'
          f'</g>')
    a(f'<text x="{W/2}" y="326" font-size="13" text-anchor="middle" fill="{t["muted"]}">'
      f'{d["total"]:,} contributions in the last year</text>')
    a(f'<line x1="32" y1="344" x2="{W-32}" y2="344" stroke="{t["muted"]}" stroke-opacity=".25"/>')

    # languages
    a(f'<text x="{W/2}" y="374" font-size="15" font-weight="700" letter-spacing="5" '
      f'text-anchor="middle" fill="{t["title"]}">TOP.LANGUAGES</text>')
    total = sum(v[0] for _, v in d["langs"]) or 1
    bx, bw = 32, W - 64
    for i, (name, (size, color)) in enumerate(d["langs"]):
        pct = size / total * 100
        y = lang_top + 12 + i * 48
        color = color or FALLBACK_COLORS[i % len(FALLBACK_COLORS)]
        a(f'<g class="fade" style="animation-delay:{.2 + i * .1:.2f}s">'
          f'<circle cx="{bx+6}" cy="{y-5}" r="6" fill="{color}"/>'
          f'<text x="{bx+22}" y="{y}" font-size="17" fill="{t["text"]}">{escape(name)}</text>'
          f'<text x="{bx+bw}" y="{y}" font-size="17" text-anchor="end" fill="{t["muted"]}">{pct:.1f}%</text>'
          f'<rect x="{bx}" y="{y+12}" width="{bw}" height="8" rx="4" fill="{t["track"]}" fill-opacity=".6"/>'
          f'<rect class="bar" style="animation-delay:{.4 + i * .1:.2f}s" x="{bx}" y="{y+12}" '
          f'width="{max(pct / 100 * bw, 6):.1f}" height="8" rx="4" fill="{color}"/></g>')
    a(f'<text x="{W/2}" y="{H-22}" font-size="12" text-anchor="middle" fill="{t["muted"]}">'
      f'updated {datetime.now(timezone.utc):%Y-%m-%d} · since {d["since"]}</text>')
    a('</svg>')
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--user", default=os.environ.get("GITHUB_ACTOR", "Embergenov-Nurmurat"))
    p.add_argument("--out", default=".")
    p.add_argument("--demo", action="store_true")
    p.add_argument("--festive", choices=["auto", "on", "off"], default="auto",
                   help="New Year decorations (auto = Nov 15 - Jan 15)")
    p.add_argument("--today", help="override date/time, e.g. 2026-12-20T14:30 (for testing)")
    p.add_argument("--tz", type=float, default=5,
                   help="UTC offset (hours) used for the New Year countdown, default 5 = Tashkent")
    args = p.parse_args()
    tz = timezone(timedelta(hours=args.tz))
    now = datetime.fromisoformat(args.today).replace(tzinfo=tz) if args.today else datetime.now(tz)
    fest = {"on": True, "off": False}.get(args.festive, festive.is_festive(now.date()))
    data = demo_data() if args.demo else fetch(args.user, os.environ["GITHUB_TOKEN"])
    os.makedirs(args.out, exist_ok=True)
    for name, theme in THEMES.items():
        def write(fname, text):
            path = os.path.join(args.out, fname)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            print("wrote", path)
        write(f"stats-{name}.svg", render(data, theme, args.user, name, fest))
        write(f"festive-{name}.svg",
              festive.strip_svg(theme, name, now) if fest else festive.empty_svg())
        banner = os.path.join(args.out, f"{name}.svg")
        if os.path.exists(banner):
            festive.apply_to_banner(banner, name, theme, fest)
            print("banner", banner, "festive" if fest else "plain")


if __name__ == "__main__":
    main()
