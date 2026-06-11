# CLAUDE.md — AMT Skills Catalog

Guidance for Claude Code (and the `@claude` GitHub Action) when working in this repo.

## What this is
A small static website (plain HTML/CSS/JS, no framework, no build step) that showcases
AMT's Claude Code skills. It does **not** create skills — it lists ones already published
to GitHub.

## The golden rule
**Edit `catalog.config.json` only. Never hand-edit `skills.json`.**
`skills.json` is GENERATED from the config by `scripts/sync-skills.py` (which pulls each
skill's name/description from its `SKILL.md`). Hand-editing it will be overwritten.

## To add or change a skill
1. Edit `catalog.config.json`:
   - **A skill we authored** → add to the `"mine"` array. Required: `slug`, `ref`
     (next `AMT-SKL-00N`), `tags`, `repo`, `install`, `status`. Do **not** write
     `name`/`summary`/`use_when` — they come from the skill's `SKILL.md` automatically
     (override only if you must).
   - **A third-party skill** → add to the `"uses"` array: `name`, `summary`, `author`, `link`.
2. Regenerate (or let CI do it on push to `main`):
   ```bash
   python3 scripts/sync-skills.py
   ```
3. Commit `catalog.config.json` **and** `skills.json` together.

When opening a PR for a teammate's request, change only `catalog.config.json`, run the
helper, and include the regenerated `skills.json` in the same PR.

## Curation
Only skills in `catalog.config.json` are published. The dozens of installed third-party
skills are NOT listed unless explicitly added to `"uses"` with author credit.

## Don't
- Don't commit secrets, `.env`, or local tooling output (`.claude-flow/`, `.swarm/` are gitignored — keep it that way).
- Don't add a build framework; this is intentionally a zero-build static site.
- Don't hardcode brand colors — the theme variables live in `styles.css`.

## Layout
- `catalog.config.json` — the curated allow-list (edit this)
- `scripts/sync-skills.py` — generator (`--check` verifies freshness, `--offline` skips network)
- `skills.json` — generated data the page loads
- `index.html`, `styles.css`, `app.js` — the page (AMT theme, light + dark)
- `public/` — AMT logos (light + dark), favicon
- `.github/workflows/` — `build-catalog.yml` (auto-regenerate) and `claude.yml` (@claude bot)
- `docs/TEAM-GUIDE.md` — how teammates add skills without a terminal
