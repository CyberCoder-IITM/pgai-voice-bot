# PGAI Patient Voice Bot

Automated voice bot that calls Pretty Good AI's test line and simulates
realistic patient conversations to evaluate agent quality and find bugs.

## Architecture

See ARCHITECTURE.md for full system design and decision rationale.

## Quick Start

```bash
python make_calls.py
```

## Setup

### 1. Accounts needed

- Twilio: twilio.com/try-twilio
- Deepgram: console.deepgram.com
- Groq: console.groq.com
- ngrok: ngrok.com/download

### 2. Install

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in your keys
```

### 3. Start ngrok

```bash
ngrok http 8000
# Copy the https URL into PUBLIC_URL in .env
```

### 4. Start server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Run all 10 calls

```bash
python make_calls.py
```

### 6. Download recordings

```bash
python download_recordings.py
```

## Scenarios

| #   | Name                 | Tests                         |
| --- | -------------------- | ----------------------------- |
| 1   | new_appointment      | Standard scheduling           |
| 2   | reschedule           | Change existing appointment   |
| 3   | medication_refill    | Refill workflow               |
| 4   | cancel_appointment   | Cancellation handling         |
| 5   | practice_info        | Hours and insurance questions |
| 6   | weekend_request      | Edge: closed on weekends      |
| 7   | elderly_patient      | Edge: slow confused speaker   |
| 8   | barge_in_impatient   | Edge: interruptions           |
| 9   | reluctant_caller     | Edge: private health concern  |
| 10  | controlled_substance | Edge: lost prescription       |

## Cost

Under $1 total for all 10 calls.
