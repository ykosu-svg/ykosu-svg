#!/usr/bin/env python3
"""Collect public GitHub stats -> data/stats.json (no token required)."""
import json, os, re, sys, datetime
import requests
from bs4 import BeautifulSoup

USER = os.environ.get("GH_USER", "ykosu-svg")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAD = {"User-Agent": f"{USER}-profile-art", "Accept": "application/vnd.github+json"}
if os.environ.get("GITHUB_TOKEN"):
    HEAD["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]


def api(path):
    r = requests.get("https://api.github.com" + path, headers=HEAD, timeout=30)
    r.raise_for_status()
    return r.json()


def contributions():
    """Scrape the public contribution calendar fragment (no auth needed)."""
    r = requests.get(f"https://github.com/users/{USER}/contributions",
                     headers={"User-Agent": HEAD["User-Agent"]}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    h = soup.find(["h2", "h1"])
    total = 0
    if h:
        m = re.search(r"([\d,]+)\s+contribution", h.get_text())
        if m:
            total = int(m.group(1).replace(",", ""))
    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        d = td.get("data-date")
        if not d:
            continue
        days.append({"date": d, "count": int(td.get("data-level", 0) or 0)})
    best = 0
    streak = 0
    run = 0
    for d in days:
        if d["count"] > 0:
            run += 1
            best = max(best, run)
        else:
            run = 0
    for d in reversed(days):
        if d["count"] > 0:
            streak += 1
        elif streak:
            break
    return {"total_year": total, "longest_streak": best, "current_streak": streak,
            "active_days": sum(1 for d in days if d["count"] > 0)}


def main():
    user = api(f"/users/{USER}")
    repos = api(f"/users/{USER}/repos?per_page=100&sort=updated")
    repos = [r for r in repos if not r.get("fork")]
    listed = [r for r in repos if r["name"].lower() != USER.lower()]

    langs = {}
    for r in repos:
        if r.get("language"):
            langs[r["language"]] = langs.get(r["language"], 0) + 1

    data = {
        "user": USER,
        "name": user.get("name") or USER,
        "created_at": (user.get("created_at") or "")[:10],
        "public_repos": len(repos),
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "stars_received": sum(r.get("stargazers_count", 0) for r in repos),
        "languages": dict(sorted(langs.items(), key=lambda kv: -kv[1])),
        "repos": [
            {"name": r["name"], "language": r.get("language") or "-",
             "stars": r.get("stargazers_count", 0), "updated": (r.get("pushed_at") or "")[:10],
             "description": (r.get("description") or "")[:70]}
            for r in listed[:6]
        ],
        "contributions": contributions(),
        "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }
    out = os.path.join(ROOT, "data", "stats.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(data, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("wrote", out)


if __name__ == "__main__":
    main()
