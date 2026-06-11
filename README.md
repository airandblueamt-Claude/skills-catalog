# AMT — Claude Skills Catalog

A small static website that showcases the Claude Code skills authored by AMT
(`airandblueamt-Claude`), plus a credited list of third-party skills we build on.

**Stack:** plain HTML + CSS + vanilla JS. No framework, no build step. The catalog
content is a single curated file — [`skills.json`](skills.json) — so adding a skill
is one edit and a `git push`.

## Run it locally

Any static file server works (the page fetches `skills.json`, so opening the file
directly with `file://` won't load data — use a server):

```bash
cd skills-catalog
python3 -m http.server 8000
# then open http://localhost:8000
```

## Add or update a skill (the whole workflow)

1. Open [`skills.json`](skills.json).
2. **A skill you authored** → add an object to the `"mine"` array:
   ```json
   {
     "slug": "my-skill",
     "ref": "AMT-SKL-002",
     "name": "My Skill",
     "summary": "One-paragraph description (lift it from the skill's SKILL.md).",
     "use_when": "When to reach for it.",
     "tags": ["Tag A", "Tag B"],
     "repo": "https://github.com/airandblueamt-Claude/my-skill",
     "install": "git clone … ~/.claude/skills/my-skill && cd ~/.claude/skills/my-skill && bash install.sh",
     "status": "public"
   }
   ```
3. **A third-party skill you recommend** → add to the `"uses"` array
   (`name`, `summary`, `author`, `link`).
4. Commit and push. Vercel redeploys automatically.

> Curation is intentional: only skills listed in `skills.json` appear. Installed
> third-party skills are never published unless you add them to `"uses"` with credit.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Page structure (masthead, two sections, title-block footer) |
| `styles.css` | The drafting / spec-sheet theme |
| `app.js` | Renders cards + rows from `skills.json`; copy-install button |
| `skills.json` | **Source of truth** — the curated catalog |
| `public/favicon.svg` | Crop-mark favicon |

## Deploy (Vercel)

This is a static site — no build command, output directory is the project root.
Link the repo once in Vercel; thereafter every push to `main` ships. (See the
project's deploy notes / ask Claude Code to wire up the Vercel project.)
