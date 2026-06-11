# AMT — Claude Skills Catalog

A small static website that showcases the Claude Code skills authored by AMT
(`airandblueamt-Claude`), plus a credited list of third-party skills we build on.

**Stack:** plain HTML + CSS + vanilla JS. No framework. The catalog is driven by a
curated allow-list — [`catalog.config.json`](catalog.config.json) — and a tiny helper
(`scripts/sync-skills.py`) that pulls each skill's name/description from its `SKILL.md`
and writes [`skills.json`](skills.json) (the file the page loads). You edit the config,
run the helper, and push.

## Run it locally

Any static file server works (the page fetches `skills.json`, so opening the file
directly with `file://` won't load data — use a server):

```bash
cd skills-catalog
python3 -m http.server 8000
# then open http://localhost:8000
```

## Add or update a skill (the whole workflow)

1. Open [`catalog.config.json`](catalog.config.json).
2. **A skill you authored** → add an object to the `"mine"` array. Only the curated
   fields are required — `name`, `summary` and `use_when` are pulled from the skill's
   `SKILL.md` automatically:
   ```json
   {
     "slug": "my-skill",
     "ref": "AMT-SKL-003",
     "tags": ["Tag A", "Tag B"],
     "repo": "https://github.com/airandblueamt-Claude/my-skill",
     "install": "git clone … ~/.claude/skills/my-skill",
     "status": "public"
   }
   ```
   The skill folder defaults to `~/.claude/skills/<slug>`; set `"skill_dir"` to point
   elsewhere. To override the auto-pulled text, just add `name` / `summary` /
   `use_when` to the entry — explicit values win.
3. **A third-party skill you recommend** → add to the `"uses"` array
   (`name`, `summary`, `author`, `link`) — these are manual (no SKILL.md to read).
4. Regenerate and push:
   ```bash
   python3 scripts/sync-skills.py       # reads SKILL.md → writes skills.json
   git add catalog.config.json skills.json
   git commit -m "Add my-skill to catalog"
   git push                             # Vercel redeploys automatically
   ```
   `python3 scripts/sync-skills.py --check` fails if `skills.json` is stale (handy in CI).

> Curation is intentional: only skills listed in `catalog.config.json` appear. Installed
> third-party skills are never published unless you add them to `"uses"` with credit.
> `skills.json` is **generated** — don't hand-edit it; edit the config and re-run the helper.

## Files

| File | Purpose |
|------|---------|
| `catalog.config.json` | **Edit this** — the curated allow-list (what gets published) |
| `scripts/sync-skills.py` | Pulls SKILL.md frontmatter → generates `skills.json` |
| `skills.json` | Generated data the page loads (don't hand-edit) |
| `index.html` | Page structure (masthead, two sections, AMT footer) |
| `styles.css` | AMT brand theme (light + dark) |
| `app.js` | Renders cards + rows from `skills.json`; theme toggle; copy-install |
| `public/` | AMT logo (light + dark), favicon |

## Deploy (Vercel)

This is a static site — no build command, output directory is the project root.
Link the repo once in Vercel; thereafter every push to `main` ships. (See the
project's deploy notes / ask Claude Code to wire up the Vercel project.)
