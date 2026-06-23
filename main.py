"""
Pretty Good AI -- Patient Voice Bot
=====================================
Stack: Twilio Media Streams -> Groq Whisper STT -> Groq LLM -> Deepgram TTS -> Twilio

Flow:
  1. make_calls.py triggers outbound PSTN call via Twilio
  2. Twilio streams G.711 ulaw audio to our FastAPI WebSocket
  3. We buffer inbound audio and detect silence using RMS energy
  4. When agent finishes speaking (silence detected), we transcribe via Groq Whisper
  5. Transcript goes to Groq Llama-3.3-70B acting as the patient persona
  6. Patient response text goes to Deepgram TTS to generate voice audio
  7. Audio converted to mulaw and streamed back to Twilio
"""

import asyncio
import audioop
import base64
import io
import json
import os
import wave
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import JSONResponse, PlainTextResponse
from groq import Groq
from twilio.rest import Client
from twilio.twiml.voice_response import Connect, Stream, VoiceResponse

from scenarios import SCENARIOS, build_system_prompt

# ── Config ─────────────────────────────────────────────────────────────────────
TWILIO_SID    = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_TOKEN  = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_NUMBER = os.environ["TWILIO_PHONE_NUMBER"]
DEEPGRAM_KEY  = os.environ["DEEPGRAM_API_KEY"]
GROQ_KEY      = os.environ["GROQ_API_KEY"]
PUBLIC_URL    = os.environ["PUBLIC_URL"].rstrip("/")

TARGET_NUMBER = "+18054398008"
DG_TTS_URL    = "https://api.deepgram.com/v1/speak?model=aura-asteria-en&encoding=linear16&sample_rate=8000"

twilio  = Client(TWILIO_SID, TWILIO_TOKEN)
groq_cl = Groq(api_key=GROQ_KEY)
app     = FastAPI(title="PGAI Patient Bot")

Path("transcripts").mkdir(exist_ok=True)
Path("recordings").mkdir(exist_ok=True)

# VAD settings
SILENCE_THRESHOLD = 200   # RMS below this = silence
SILENCE_FRAMES    = 50    # ~1 second of silence at 20ms/frame = end of turn
MIN_SPEECH_FRAMES = 8     # minimum speech frames before we try to transcribe


# ── Helpers ────────────────────────────────────────────────────────────────────

def mulaw_to_wav(mulaw_bytes: bytes) -> bytes:
    """Convert G.711 ulaw audio to WAV format for Groq Whisper."""
    pcm = audioop.ulaw2lin(mulaw_bytes, 2)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(pcm)
    return buf.getvalue()


def pcm16_to_mulaw_b64(pcm_bytes: bytes) -> str:
    """Convert linear16 PCM from Deepgram TTS to G.711 ulaw base64 for Twilio."""
    mulaw = audioop.lin2ulaw(pcm_bytes, 2)
    return base64.b64encode(mulaw).decode()


async def transcribe(mulaw_bytes: bytes) -> str:
    """Transcribe audio using Groq Whisper."""
    try:
        wav = mulaw_to_wav(mulaw_bytes)
        result = groq_cl.audio.transcriptions.create(
            file=("audio.wav", wav),
            model="whisper-large-v3-turbo",
            response_format="text",
        )
        return result.strip() if result else ""
    except Exception as e:
        print(f"[WHISPER ERROR] {e}")
        return ""


async def tts(text: str) -> Optional[bytes]:
    """Call Deepgram TTS REST API and return raw PCM audio bytes."""
    headers = {
        "Authorization": f"Token {DEEPGRAM_KEY}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=15.0) as http:
        r = await http.post(DG_TTS_URL, headers=headers, json={"text": text})
    if r.status_code == 200:
        return r.content
    print(f"[TTS ERROR] {r.status_code}: {r.text[:200]}")
    return None


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "scenarios": len(SCENARIOS)}


@app.api_route("/twiml/{scenario_id}", methods=["GET", "POST"])
async def twiml_handler(request: Request, scenario_id: str):
    ws_base = PUBLIC_URL.replace("https://", "wss://").replace("http://", "ws://")
    response = VoiceResponse()
    connect = Connect()
    stream = Stream(url=f"{ws_base}/stream/{scenario_id}")
    connect.append(stream)
    response.append(connect)
    return PlainTextResponse(str(response), media_type="text/xml")


@app.post("/call-status")
async def call_status(request: Request):
    form = await request.form()
    print(
        f"[STATUS] SID={form.get('CallSid','?')} "
        f"status={form.get('CallStatus','?')} "
        f"duration={form.get('CallDuration','?')}s"
    )
    return JSONResponse({"ok": True})


# ── WebSocket bridge ───────────────────────────────────────────────────────────

@app.websocket("/stream/{scenario_id}")
async def stream_handler(websocket: WebSocket, scenario_id: str):
    await websocket.accept()

    scenario   = SCENARIOS.get(scenario_id, SCENARIOS["1"])
    sys_prompt = build_system_prompt(scenario)
    history    = []
    transcript = []
    stream_sid: Optional[str] = None
    is_speaking = False   # True while patient TTS is playing

    print(f"\n{'='*60}")
    print(f"[CALL START] Scenario {scenario_id}: {scenario['name']}")
    print(f"[PERSONA]    {scenario['patient']}")
    print(f"[GOAL]       {scenario['goal']}")
    print(f"{'='*60}")

    response_lock = asyncio.Lock()
    speech_queue: asyncio.Queue = asyncio.Queue()

    async def patient_respond(agent_text: str):
        nonlocal is_speaking
        async with response_lock:
            if not agent_text.strip() or stream_sid is None:
                return

            print(f"  AGENT  : {agent_text}")
            transcript.append({"speaker": "PGAI AGENT", "text": agent_text})
            history.append({"role": "user", "content": agent_text})

            # ── Groq LLM: patient response ────────────────────────────────────
            completion = groq_cl.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": sys_prompt}, *history],
                max_tokens=120,
                temperature=0.75,
            )
            patient_text = completion.choices[0].message.content.strip()
            history.append({"role": "assistant", "content": patient_text})
            transcript.append({"speaker": "PATIENT (bot)", "text": patient_text})
            print(f"  PATIENT: {patient_text}")

            # ── Deepgram TTS: text -> PCM -> mulaw -> Twilio ──────────────────
            pcm = await tts(patient_text)
            if pcm:
                is_speaking = True
                mulaw_b64   = pcm16_to_mulaw_b64(pcm)
                mulaw_bytes = base64.b64decode(mulaw_b64)
                chunk_size  = 160 * 10
                for i in range(0, len(mulaw_bytes), chunk_size):
                    chunk = mulaw_bytes[i : i + chunk_size]
                    await websocket.send_text(json.dumps({
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {"payload": base64.b64encode(chunk).decode()},
                    }))
                    await asyncio.sleep(0.005)
                await asyncio.sleep(0.5)  # brief pause after patient finishes
                is_speaking = False

    async def listen_and_buffer():
        """Receive Twilio audio, detect silence, queue complete utterances."""
        nonlocal stream_sid
        audio_buffer  = bytearray()
        silence_count = 0
        speech_count  = 0

        try:
            async for raw in websocket.iter_text():
                msg = json.loads(raw)
                ev  = msg.get("event")

                if ev == "start":
                    stream_sid = msg["start"]["streamSid"]
                    print(f"[TWILIO] Stream connected: {stream_sid}")

                elif ev == "media":
                    if msg["media"].get("track") != "inbound":
                        continue
                    if is_speaking:
                        # Ignore audio while patient is talking
                        audio_buffer.clear()
                        silence_count = 0
                        speech_count  = 0
                        continue

                    chunk    = base64.b64decode(msg["media"]["payload"])
                    pcm      = audioop.ulaw2lin(chunk, 2)
                    rms      = audioop.rms(pcm, 2)

                    if rms > SILENCE_THRESHOLD:
                        audio_buffer.extend(chunk)
                        speech_count  += 1
                        silence_count  = 0
                    else:
                        if speech_count > 0:
                            audio_buffer.extend(chunk)
                            silence_count += 1

                        if silence_count >= SILENCE_FRAMES and speech_count >= MIN_SPEECH_FRAMES:
                            await speech_queue.put(bytes(audio_buffer))
                            audio_buffer  = bytearray()
                            silence_count = 0
                            speech_count  = 0

                elif ev == "stop":
                    print("[TWILIO] Stream stopped")
                    break

        except Exception as e:
            print(f"[TWILIO ERROR] {e}")

    async def process_queue():
        """Pick items from queue: strings go direct, bytes get transcribed first."""
        while True:
            item = await speech_queue.get()
            if isinstance(item, str):
                # Injected text (opening line) -- respond directly
                await patient_respond(item)
            elif isinstance(item, bytes):
                # Raw audio -- transcribe first
                text = await transcribe(item)
                if text:
                    await patient_respond(text)

    try:
        await asyncio.gather(
            listen_and_buffer(),
            process_queue(),
        )
    except Exception as e:
        print(f"[SESSION ERROR] {e}")
    finally:
        ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"transcripts/transcript_{scenario_id}_{scenario['name']}_{ts}.txt"
        with open(fname, "w") as f:
            f.write(f"Scenario {scenario_id}: {scenario['name']}\n")
            f.write(f"Patient  : {scenario['patient']}\n")
            f.write(f"Goal     : {scenario['goal']}\n")
            f.write(f"Date/Time: {ts}\n")
            f.write("=" * 60 + "\n\n")
            for turn in transcript:
                f.write(f"[{turn['speaker']}]:\n{turn['text']}\n\n")
        print(f"[SAVED] {fname}  ({len(transcript)} turns)")