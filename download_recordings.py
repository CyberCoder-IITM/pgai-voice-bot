"""
Download call recordings from Twilio as mp3 after calls complete.
Run this about 5 minutes after your last call finishes.

Usage: python download_recordings.py
"""

import os
import time
from pathlib import Path

import requests
from twilio.rest import Client

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
Path("recordings").mkdir(exist_ok=True)


def download_recordings(limit: int = 25):
    recordings = client.recordings.list(limit=limit)
    print(f"Found {len(recordings)} recording(s)")

    for rec in recordings:
        safe_date = rec.date_created.strftime("%Y%m%d_%H%M%S")
        filename = f"recordings/call_{rec.call_sid[:12]}_{safe_date}.mp3"

        if Path(filename).exists():
            print(f"  [SKIP]  {filename}")
            continue

        mp3_uri = rec.uri.replace(".json", ".mp3")
        url = f"https://api.twilio.com{mp3_uri}"
        r = requests.get(url, auth=(
            os.environ["TWILIO_ACCOUNT_SID"],
            os.environ["TWILIO_AUTH_TOKEN"]
        ))

        if r.status_code == 200:
            with open(filename, "wb") as f:
                f.write(r.content)
            print(f"  [SAVED] {filename}  ({len(r.content)//1024} KB)")
        else:
            print(f"  [ERR]   {rec.call_sid}: HTTP {r.status_code}")

        time.sleep(0.5)


if __name__ == "__main__":
    download_recordings()