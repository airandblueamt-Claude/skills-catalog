#!/usr/bin/env python3
"""
sync-skills.py — generate skills.json from catalog.config.json.

For each skill listed under "mine", reads its SKILL.md frontmatter and fills in
`name`, `summary` and `use_when` automatically — so nobody has to retype a
description. The SKILL.md is read from, in order:
  1. a local checkout  (~/.claude/skills/<slug>/SKILL.md, or "skill_dir"), then
  2. the skill's GitHub repo  (raw.githubusercontent.com, from "repo").
So it works on an author's machine AND in CI / on a teammate's machine where the
skill isn't installed locally.

Curated fields — ref / tags / repo / install / status — always come from the
config. Anything you set explicitly in the config wins over the auto-pulled value.

Usage:
    python3 scripts/sync-skills.py            # regenerate skills.json
    python3 scripts/sync-skills.py --check    # exit 1 if skills.json is out of date
    python3 scripts/sync-skills.py --offline  # never hit the network (local only)
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONFIG = os.path.join(ROOT, "catalog.config.json")
OUTPUT = os.path.join(ROOT, "skills.json")

DEFAULT_BRANCHES = ("main", "master")
OFFLINE = "--offline" in sys.argv

# tokens to uppercase when prettifying a slug into a display name
ACRONYMS = {
    "amt", "pas", "iptv", "av", "pdf", "boq", "kfuh", "css", "json",
    "en", "ar", "rtl", "hdmi", "dvb", "oem", "ui", "ux", "api", "cli",
}


def parse_frontmatter(text: str) -> dict:
    """Parse YAML-ish frontmatter (--- ... ---). Tolerates quoted/unquoted values."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}
    fields = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        val = val.strip()
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            val = val[1:-1]
        fields[key.strip()] = val.strip()
    return fields


def raw_url(repo: str, branch: str) -> str:
    """github.com/<owner>/<name>(.git) -> raw SKILL.md URL for a branch."""
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", repo or "")
    if not m:
        return ""
    return f"https://raw.githubusercontent.com/{m.group(1)}/{m.group(2)}/{branch}/SKILL.md"


def fetch_text(url: str, timeout: int = 12) -> str | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "amt-catalog-sync"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None


def load_skill_md(entry: dict) -> tuple[str, str]:
    """Return (text, source). Try a local checkout first, then the GitHub repo."""
    slug = entry["slug"]
    local = os.path.join(
        os.path.expanduser(entry.get("skill_dir", f"~/.claude/skills/{slug}")),
        "SKILL.md",
    )
    if os.path.isfile(local):
        with open(local, encoding="utf-8") as fh:
            return fh.read(), "local"
    if OFFLINE:
        return "", "offline (no local copy)"
    branches = [entry["branch"]] if entry.get("branch") else list(DEFAULT_BRANCHES)
    for b in branches:
        url = raw_url(entry.get("repo", ""), b)
        if not url:
            break
        txt = fetch_text(url)
        if txt:
            return txt, f"repo@{b}"
    return "", "not found"


def prettify(slug: str) -> str:
    words = re.split(r"[-_\s]+", slug)
    return " ".join(w.upper() if w.lower() in ACRONYMS else w.capitalize() for w in words)


def split_summary(description: str) -> tuple[str, str | None]:
    """Split a SKILL.md description into (summary, use_when) on 'Use when'."""
    m = re.search(r"\bUse when\b[:\s]*", description, re.IGNORECASE)
    if not m:
        return description.strip(), None
    summary = description[: m.start()].strip().rstrip(".").strip() + "."
    use_when = description[m.end():].strip()
    if use_when:
        use_when = use_when[0].upper() + use_when[1:]
    return summary, (use_when or None)


def build_mine(entry: dict) -> dict:
    slug = entry["slug"]
    text, source = load_skill_md(entry)
    fm = parse_frontmatter(text) if text else {}
    if not fm and not entry.get("summary"):
        print(f"  ! {slug}: no SKILL.md found ({source}) and no summary in config.")
    desc = fm.get("description", "")
    auto_summary, auto_use_when = split_summary(desc) if desc else ("", None)

    name = entry.get("name") or (prettify(fm["name"]) if fm.get("name") else prettify(slug))
    card = {
        "slug": slug,
        "ref": entry.get("ref", ""),
        "name": name,
        "summary": entry.get("summary") or auto_summary,
        "use_when": entry.get("use_when", auto_use_when),
        "tags": entry.get("tags", []),
        "repo": entry.get("repo", ""),
        "install": entry.get("install", ""),
        "status": entry.get("status", "public"),
    }
    if card["use_when"] is None:
        del card["use_when"]
    print(f"  ✓ {slug}: '{name}' (from {source})")
    return card


def generate(config: dict) -> dict:
    print("Syncing skills from SKILL.md frontmatter …")
    return {
        "_note": "GENERATED by scripts/sync-skills.py from catalog.config.json — edit the config, not this file.",
        "owner": config.get("owner", {}),
        "mine": [build_mine(e) for e in config.get("mine", [])],
        "uses": config.get("uses", []),
    }


def main() -> int:
    with open(CONFIG, encoding="utf-8") as fh:
        config = json.load(fh)
    rendered = json.dumps(generate(config), ensure_ascii=False, indent=2) + "\n"

    if "--check" in sys.argv:
        current = open(OUTPUT, encoding="utf-8").read() if os.path.isfile(OUTPUT) else ""
        if current != rendered:
            print("✗ skills.json is OUT OF DATE — run: python3 scripts/sync-skills.py")
            return 1
        print("✓ skills.json is up to date.")
        return 0

    with open(OUTPUT, "w", encoding="utf-8") as fh:
        fh.write(rendered)
    data = json.loads(rendered)
    print(f"Wrote {OUTPUT} — {len(data['mine'])} mine, {len(data['uses'])} uses.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
