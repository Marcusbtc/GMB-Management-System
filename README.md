# Google My Business Manager

A Streamlit platform to monitor Google Business Profile (GBP) performance, analyze reviews, publish posts, and export reports.

Built for:
- Marketing agencies
- Local business owners
- Customer support and sales teams

## What you can do

- Track profile views and actions
- Analyze search keywords and trends
- Review customer feedback and generate AI reply suggestions (optional)
- Publish posts directly to GBP
- Upload image from your computer via Google Drive and attach it to the post
- Run profile health checks
- Export PDF reports

## Quick Start (5 minutes)

1. Open the app at `http://localhost:8501`.
2. Click **Login with Google**.
3. Authorize access to your Google Business Profile.
4. In the sidebar, choose a business in **Select Business**.
5. Choose a date range.
6. Click **Fetch Data**.
7. Use tabs: **Overview**, **Reviews**, **Posts**, **Health**, **Create Post**.

## Create Post with image from your computer

1. Open **Create Post**.
2. Set post details (type, language code, text, optional CTA).
3. In **Image Source**, choose **Upload from computer (Drive)**.
4. Select the image file.
5. Browse Drive folders and select where the file will be saved.
6. Click **Upload image to Drive**.
7. After URL is ready, click **Publish Now**.

## Security basics

- Never share `client_secret.json`.
- Never expose API keys in chat, email, or screenshots.
- Keep Drive/GBP access limited to required users.

## Technical Setup (Support)

### Requirements

- Python 3.10+
- Google OAuth credentials

### Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Credentials

Provide OAuth in one of these ways:

1. Put `client_secret.json` in project root
2. Configure `.streamlit/secrets.toml` with OAuth `web` object
3. Set OAuth env vars in `.env` (based on `.env.example`):
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_REDIRECT_URI`
   - `GOOGLE_AUTH_URI`
   - `GOOGLE_TOKEN_URI`

Required scopes:
- `https://www.googleapis.com/auth/business.manage`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/drive.metadata.readonly`

Optional AI key:

```bash
export GEMINI_API_KEY="your_key_here"
```

### Run

```bash
streamlit run app.py
```

Open: `http://localhost:8501`

## Development

Install dev tools:

```bash
pip install -r requirements-dev.txt
```

Run checks:

```bash
ruff check src tests app.py auth.py
pytest
python -m py_compile app.py auth.py data_fetcher.py drive_helper.py
```

Utility/debug scripts are in `tools/`.

## Portuguese Documentation

See [README-ptbr.md](README-ptbr.md).

## License

MIT (see `LICENSE`).
