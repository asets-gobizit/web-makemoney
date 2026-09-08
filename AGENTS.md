# AGENTS.md — web-makemoney

Operating notes for future agents working on this repo. Prefer taking safe, reversible
actions autonomously over asking for confirmation (see "Working style" below).

## What this project is
Static landing site for **makemoney.gobizit.ai** ("Make Money AI"). Plain HTML/CSS/JS,
**no build step**. A few optional Python scripts generate assets (`generate_hero_video.py`,
`generate_picsart_background.py`) and need `pillow` / `requests` / `ffmpeg`.

## Hosting & deploy (current — as of 2026-09-08)
- **Production host: Vercel.** Project `web-makemoney` in team **`nio-team`**, git-linked to
  `asets-gobizit/web-makemoney`. Every push to `main` auto-deploys to production.
- **Custom domain:** `makemoney.gobizit.ai`, DNS on **Cloudflare** (zone `gobizit.ai`):
  `CNAME makemoney → cname.vercel-dns.com`, **Proxy = DNS only** (grey cloud). SSL is
  auto-issued by Vercel.
- The site was **migrated off GitHub Pages → Vercel on 2026-09-08**; the repo no longer
  contains a `CNAME` file. `web-makemoney.vercel.app` still resolves and redirects to the
  custom domain.

## Local preview
Serve the static files (see `.cursor/environment.json`):

```bash
python3 -m http.server 8000
```

## Runbook: migrate a static site from GitHub Pages → Vercel (nio-team)
Reusable for the other `asets-gobizit` static sites.
1. Push the repo to GitHub. **Grant the Vercel GitHub App access to the repo** (GitHub → org
   `asets-gobizit` → Settings → Installed GitHub Apps → Vercel → Configure → add the repo, or
   use "Adjust GitHub App Permissions" from Vercel's import screen). This is the usual blocker.
2. Vercel → team **`nio-team`** → Add New → Project → **Import** the repo. Framework preset
   **Other** (static), **no build command**, output = repo root. Deploy.
3. Project → **Settings → Domains** → add the custom subdomain (e.g. `makemoney.gobizit.ai`).
4. **Cloudflare** (zone `gobizit.ai`): point the subdomain `CNAME → cname.vercel-dns.com`,
   **Proxy = DNS only**. Remove old GitHub Pages records (A records `185.199.108–111.153`, or
   the CNAME to `asets-gobizit.github.io`).
5. Wait for Vercel to issue SSL, then **delete the repo `CNAME` file** and clear the repo
   **Settings → Pages** custom domain so GitHub Pages releases the domain.

## Gotchas for future agents (learned the hard way)
- The **Cursor↔Vercel MCP token is permission-limited on `nio-team` (hobby plan)**: it can
  create projects but frequently returns **403/404 when reading or managing** them, and
  `list_projects` / `get_project` may omit real projects. Do **not** conclude a project is
  missing or a deploy failed based on the Vercel MCP alone.
- **Verify Vercel deploys reliably via GitHub + HTTP instead:**
  - `gh api repos/asets-gobizit/<repo>/commits/main/status` → Vercel statuses carry the
    `target_url`; `gh api repos/asets-gobizit/<repo>/deployments/<id>/statuses` carries the
    live `environment_url`.
  - `curl -sI https://<project>.vercel.app/` — the public production alias should be `200`
    with `server: Vercel`. The immutable `*-<hash>-nio-team.vercel.app` URLs sit behind
    Vercel Authentication (302 → login), so use the clean production alias for public checks.
- **Agents have no Cloudflare access here.** DNS edits are manual by the user; provide exact
  record values.
- Retrying a Vercel import can spawn **duplicate name-suffixed projects** (e.g.
  `web-makemoney-7mzq`). Keep the clean-named project and delete the extras.

## Working style
Neo (Operations) prefers agents to **just do the things they safely can** — take action and
report, rather than asking for confirmation on every low-risk, reversible step. Still confirm
before destructive/irreversible actions (e.g. deleting resources, merging PRs) unless already
told to proceed.
