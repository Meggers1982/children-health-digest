# children-health-digest

A daily children's-health news digest. A GitHub Actions cron pulls recent items
from a curated list of child-health organizations, has Claude select and
summarize the noteworthy ones, writes the result to `outputs/`, and emails it.

## How it works

`.github/workflows/daily-digest.yml` runs `scripts/main.py` at 08:00 UTC on
weekdays. Each run:

1. **Fetches** (`fetcher.py`) recent items from the feeds in
   `config/sources.json`, capped per source and deduplicated within the run.
2. **Generates the digest** (`digest_generator.py`) — one Claude call selects
   and writes up the items worth surfacing.
3. **Emails it** (`email_sender.py`) via Resend, if a recipient and API key are
   configured.
4. **Commits** the digest to `outputs/` so history accumulates in the repo.

`All Organizations.xlsx` is the working source list the feeds in
`config/sources.json` were drawn from — organization, category, press page, RSS
feed, and newsletter signup for each.

## Configuration

Edit `config/digest_config.json` and commit — the next run picks it up:

- `days_back` — how far back to look for new items (2 gives a weekend buffer).
- `max_items_per_source` — cap per source per run, so one prolific
  organization can't flood the digest.
- `min_items_to_send` — skip the email if fewer than this many items are found.
- `model` — Claude model used for generation.
- `from_email` — sender address.

Add or remove sources by editing `config/sources.json`.

## Required secrets (GitHub Actions)

Set these under Settings → Secrets and variables → Actions:

| Secret | Purpose |
| --- | --- |
| `ANTHROPIC_API_KEY` | Anthropic API key (`sk-ant-...`) for digest generation |
| `RESEND_API_KEY` | Resend key for delivery |
| `TO_EMAIL` | Recipient address — kept in a secret, not in the repo |

The recipient is read from the `TO_EMAIL` environment variable, falling back to
`to_email` in the config file if unset. Keep it in the secret so the address
stays out of a public repo.

## Running locally

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...
export RESEND_API_KEY=...     # optional — omit to skip the email
export TO_EMAIL=...           # optional — omit to skip the email
cd scripts
python3 main.py
```
