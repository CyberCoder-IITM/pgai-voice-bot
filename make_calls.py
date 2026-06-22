"""
Trigger outbound calls to the PGAI test line.

Usage:
  python make_calls.py           -- run all 10 scenarios sequentially
  python make_calls.py 1         -- run only scenario 1
  python make_calls.py 1 3 6     -- run specific scenarios
"""

import os
import sys
import time

from twilio.rest import Client

client    = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
PUBLIC_URL    = os.environ["PUBLIC_URL"].rstrip("/")
FROM_NUMBER   = os.environ["TWILIO_PHONE_NUMBER"]
TARGET_NUMBER = "+18054398008"

CALL_GAP_SECONDS = 90

def make_call(scenario_id: str) -> str:
    call = client.calls.create(
        to=TARGET_NUMBER,
        from_=FROM_NUMBER,
        url=f"{PUBLIC_URL}/twiml/{scenario_id}",
        record=True,
        recording_channels="dual",
        status_callback=f"{PUBLIC_URL}/call-status",
        status_callback_event=["completed"],
        status_callback_method="POST",
        timeout=60,
    )
    print(f"[CALL {scenario_id}] SID: {call.sid} | Status: {call.status}")
    return call.sid


def main():
    ids = sys.argv[1:] if len(sys.argv) > 1 else [str(i) for i in range(1, 11)]
    print(f"Launching {len(ids)} call(s): scenarios {ids}")

    sids = []
    for i, sid in enumerate(ids):
        call_sid = make_call(sid)
        sids.append(call_sid)
        if i < len(ids) - 1:
            print(f"  Waiting {CALL_GAP_SECONDS}s before next call...")
            time.sleep(CALL_GAP_SECONDS)

    print(f"\nDone. Call SIDs: {sids}")


if __name__ == "__main__":
    main()

