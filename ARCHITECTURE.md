# Architecture — PGAI Patient Voice Bot

## Overview

This system makes automated outbound phone calls to the Pretty Good AI test
line and conducts realistic patient conversations using an LLM-driven persona.
It records both sides of each conversation and produces transcripts for bug
analysis.

## How It Works

When make_calls.py triggers a call, Twilio places an outbound PSTN call to
the PGAI test line. Once the call connects, Twilio opens a bidirectional audio
stream to our FastAPI WebSocket server. Inbound audio from the PGAI agent
arrives as G.711 ulaw chunks at 8kHz, which we forward directly to Deepgram's
real-time STT WebSocket — no format conversion needed since Deepgram accepts
ulaw natively. When Deepgram detects the agent has finished speaking
(speech_final=True after 1.2 seconds of silence), the transcript goes to Groq's
Llama-3.3-70B model, which responds as the patient persona defined in
scenarios.py. The patient response text goes to Deepgram TTS, which returns
linear16 PCM audio that we convert to ulaw in one line using Python's stdlib
audioop module, then stream back to Twilio so the PGAI agent hears the patient.

## Key Design Decisions

Deepgram was chosen over Whisper for STT because it accepts ulaw audio
directly from Twilio with no conversion, operates as a real-time WebSocket
stream rather than batched file uploads, and has native utterance-end detection
via utterance_end_ms. Groq was chosen for LLM inference because its speed
(under 200ms for a 120-token response) keeps the patient response latency low
enough to feel natural on a phone call. The audioop conversion from linear16
to ulaw is a single stdlib call with no ffmpeg or pydub dependency, which keeps
the setup simple and cross-platform. All conversation history is maintained
across turns so the patient remembers context from earlier in the call.
