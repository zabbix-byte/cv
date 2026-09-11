## Online Resume

Personal CV site (Django). Live design at [ztrunk.space](https://ztrunk.space/).

### Deploy free on Render (from GitHub)

1. Push this repo to GitHub (already at `zabbix-byte/cv`).
2. Go to [render.com](https://render.com) → **New** → **Blueprint**.
3. Connect the `cv` repo — it picks up `render.yaml`.
4. Deploy. You get a URL like `https://cv-xxxx.onrender.com`.

Optional custom domain: Render dashboard → your service → **Settings** → **Custom Domains** → add `ztrunk.space`.

**Notes**
- Free tier sleeps after ~15 min idle (first request can take ~30s).
- `SECRET_KEY` is auto-generated; set `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` to your real domain after you attach it.
- Local scrape/Chrome image is the older `dockerfile`; production uses the slim `Dockerfile`.

### Statistics (private)

`/statistics/` stores visitor IP, city/country, pages, and time on page. The dashboard is locked with `STATS_TOKEN` (Render → Environment).

This repo is linked to Neon project `autumn-frost-04902495` (branch `production`). Locally, `npx neon link` writes `DATABASE_URL` to `.env.local` (gitignored).

On Render, add the same `DATABASE_URL` (Neon → Connection string, pooled is fine) so metrics survive deploys. Then redeploy; `bin/start.sh` runs `migrate`.

### Local

```bash
pip install -r requirements.txt
set SECRET_KEY=dev
python manage.py runserver
```
