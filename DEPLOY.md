# Deploy guide — driven from Claude Code

Claude Code is the terminal agent you run on your machine. It will run the app, push it to
GitHub, and deploy it. You can paste the **prompts** (lines after `>`) into Claude Code, or run
the raw commands yourself.

## 0. Prerequisites (one-time)
- Install Claude Code: `npm install -g @anthropic-ai/claude-code` (needs Node 18+).
- Install Python 3.12+ and Git.
- A GitHub account. (Optional) the GitHub CLI `gh`, and a free Render account.

## 1. Open the project in Claude Code
Copy the `nri_uhnw_lead_gen` folder to your computer, then:
```bash
cd path/to/nri_uhnw_lead_gen
claude
```
Claude Code reads `CLAUDE.md` automatically for context.

## 2. Run it locally first
> Prompt: "Create a Python 3.12 venv, install requirements, build the dataset, ingest, and run the app."

Equivalent commands:
```bash
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python build_dataset.py        # builds data/seed_leads.csv, watchlist.csv, Excel
python -m app.ingest           # builds data/snapshot.json
uvicorn app.main:app --reload  # open http://127.0.0.1:8000
```
You should see the directory at `/` and profiles at `/p/<slug>`.

## 3. Put it on GitHub
> Prompt: "Initialise git, commit everything, create a new private GitHub repo named nri-uhnw-lead-intel and push."

Equivalent commands:
```bash
git init && git add . && git commit -m "Initial commit: NRI/OCI UHNW lead intelligence"
gh repo create nri-uhnw-lead-intel --private --source=. --push
# (no gh? create the repo on github.com, then:)
# git remote add origin https://github.com/<you>/nri-uhnw-lead-intel.git
# git branch -M main && git push -u origin main
```
`.gitignore` already excludes `.env`, the SQLite DB, and the preview — so no secrets are pushed.

## 4. Deploy the web app (Render, one-click)
1. Go to https://dashboard.render.com → **New → Blueprint**.
2. Connect your GitHub and pick the `nri-uhnw-lead-intel` repo. Render reads `render.yaml`.
3. It creates the web service + a 1 GB disk for the DB and auto-generates `ADMIN_TOKEN`.
4. Fill the prompted env vars (all optional except where noted):
   - `SEC_USER_AGENT` = `YourFirm research you@yourfirm.com`  (enables the free SEC source)
   - `SERPER_API_KEY` = your serper.dev key  (news + appearances enrichment)
   - `APOLLO_API_KEY` = your apollo.io key   (contact + photo enrichment)
5. Click **Apply**. First build runs the Dockerfile; when live, open the Render URL.
   Health check: `/healthz`.

> Or ask Claude Code: "Walk me through deploying this repo on Render using render.yaml."

(Prefer Docker on your own box? `docker compose up --build` → http://localhost:8000.)

## 5. Turn on the weekly auto-refresh
The schedule lives in `.github/workflows/refresh.yml` (Mondays 06:00 UTC). Give it the same keys
as repo secrets so enrichment runs:
1. GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**.
2. Add: `SEC_USER_AGENT`, `SERPER_API_KEY`, `APOLLO_API_KEY`.
   - If you use a persistent DB, also add `DEPLOY_REFRESH_URL` =
     `https://<your-render-url>/admin/refresh?token=<ADMIN_TOKEN>` so the Action refreshes the DB.
3. Test it now: repo → **Actions → Weekly lead refresh → Run workflow**.

## 6. Verify
- App: open the Render URL, filter by sector/region, open a profile.
- API: `https://<your-url>/api/leads` returns JSON.
- Refresh: after the Action runs, `data/snapshot.json` shows a new commit and the app updates.

## Using Claude Code afterwards
Keep Claude Code for changes, not running — e.g.:
> "Add a LinkedIn Sales Navigator source under nri_leadgen/sources following base.py."
> "Add an email alert when a new A-Hot lead appears in the weekly refresh."
> "Tune scoring so lock-up expiries in the next 60 days score highest."
The running app + GitHub Action operate on their own; Claude Code is your developer on call.
