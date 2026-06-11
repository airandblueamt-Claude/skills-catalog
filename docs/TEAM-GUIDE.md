# Team guide — adding skills without a terminal

Three ways to add a skill, from easiest to most hands-on. Pick whichever suits you.

---

## Option 1 — Open an issue and let Claude do it (no GitHub knowledge)
1. Go to the repo → **Issues** → **New issue** → **"➕ Add a skill to the catalog"**.
2. Fill the fields (skill slug, repo URL, which section).
3. After it's created, add a comment: **`@claude please add this skill to the catalog`**.
4. Claude opens a pull request with the change. A maintainer reviews and merges. Done.

*(Requires the one-time setup below. Only repo collaborators can trigger @claude.)*

---

## Option 2 — Edit one file on GitHub.com (no terminal)
1. Open **`catalog.config.json`** on GitHub → click the **pencil (Edit)** icon.
2. Add an entry to the `"mine"` array (a skill you authored):
   ```json
   {
     "slug": "my-new-skill",
     "ref": "AMT-SKL-003",
     "tags": ["Tag A", "Tag B"],
     "repo": "https://github.com/airandblueamt-Claude/my-new-skill",
     "install": "git clone https://github.com/airandblueamt-Claude/my-new-skill.git ~/.claude/skills/my-new-skill",
     "status": "public"
   }
   ```
   (For a third-party skill, add to `"uses"`: `name`, `summary`, `author`, `link`.)
3. Click **Commit changes** (commit straight to `main`, or open a PR).
4. A GitHub Action automatically reads the skill's `SKILL.md`, regenerates `skills.json`,
   and the site redeploys. **You never touch `skills.json` or run anything.**

> You don't write the name/description — they're pulled from the skill's `SKILL.md`.

---

## Option 3 — Ask Claude Code (if you have it)
Just say: **"add &lt;skill&gt; to the catalog"**. Claude edits the config, runs the
helper, and pushes.

---

## One-time setup (repo owner — do this once)

**A. Deploy the site (Vercel)** — so changes go live.
- In Claude Code: `/mcp` → `vercel` → authenticate, then ask Claude to link & deploy this repo.
- Or at vercel.com: New Project → import `skills-catalog` → Deploy (no build settings needed).
- After linking, every push to `main` auto-deploys.

**B. (Optional) Enable the `@claude` assistant — no API key, uses your Claude plan**
You do **not** need a paid API key. The `@claude` bot runs on your **Claude Pro/Max
subscription** via an OAuth token. Skip this entirely if you don't want the bot —
Options 2 and 3 above need nothing.
1. Install the Claude GitHub App: https://github.com/apps/claude → Install → select this repo.
2. Generate a subscription token: in Claude Code run **`claude setup-token`** (requires a
   Claude Pro or Max plan) and copy the token it prints.
3. Add it as a secret: repo **Settings → Secrets and variables → Actions → New repository secret**
   - Name: `CLAUDE_CODE_OAUTH_TOKEN`
   - Value: the token from step 2
4. Done. Without this secret the `@claude` workflow simply does nothing; the keyless
   paths keep working.

**C. Add teammates** — repo **Settings → Collaborators** → add them. Only collaborators
(OWNER / MEMBER / COLLABORATOR) can trigger `@claude`, which keeps API cost under control
on a public repo.

---

## How it fits together
```
edit catalog.config.json  ──push──▶  GitHub Action (build-catalog.yml)
   (web / Claude / @claude PR)          ├─ reads each skill's SKILL.md from its repo
                                        ├─ regenerates skills.json
                                        └─ commits it back  ──▶  Vercel auto-deploys
```
`skills.json` is always generated — the config is the only thing anyone edits.
