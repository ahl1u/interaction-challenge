# Shipping Email Tracker

A Python pipeline that parses HTML shipping emails, tracks order state in SQLite, and sends SMS notifications on actionable status changes.

Built this because I used to track 20+ sneaker orders simultaneously and wanted something that would just text me when something actually happened. 

Shipping emails are generally inconsistent, noisy and hard to keep track of. In this case, the useful user-facing behavior is simple: know when an order ships, goes out for delivery, gets delivered, or hits a delivery problem.


## Architecture

```text
HTML email
    → clean_html()
    → parse_email()        [OpenRouter / Claude Haiku]
    → upsert_order()       [SQLite]
    → should_send_sms()
    → send_sms()           [Twilio or DRY_RUN stdout]
    → mark_notified()

export_csv()               [SQLite → orders.csv]
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# set OPENROUTER_API_KEY at minimum
# DRY_RUN=true by default, prints SMS instead of sending
```

For real SMS, set `DRY_RUN=false` and add Twilio credentials to `.env`.

## Run

```bash
python3 main.py   # produces orders.db and orders.csv
pytest tests/
```
