# Voice Agent asynchronous task reference lab

Two deterministic Python standard-library fixtures for task ownership, cancellation, idempotency and local result delivery.

## Reproduce

Run with Python 3.10+; no installation, network, API keys, user data or real audio.

```sh
python3 lab.py
python3 durable_lab.py
```

| Fixture | Local result | Boundary |
| --- | --- | --- |
| lab.py | 6/6 | Independent foreground event loop, duplicate suppression, cancellation, session scope, allowlist, unguarded control |
| durable_lab.py | 6/6 | SQLite transaction rollback, close/reopen, composite key isolation, cancellation, replay and acknowledgment, two sequential connections |

Recorded environment: Darwin, Python 3.10.2, SQLite 3.35.5. The generated JSON results are included. The SQLite example does not test process killing, concurrent stress, real vendor protocol interoperability, audio latency, cost, production authentication, external side effects or exactly-once network delivery. The local outbox is not a provider wire payload. Do not use this teaching adapter as a production security boundary.

## Research and protocol references

- [English analysis](https://www.xbstack.com/en/ai/qwen-audio-live-voice-agent/?utm_source=github&utm_medium=referral&utm_campaign=qwen_audio_live_voice_agent&utm_content=problem_labs_repro)
- [中文完整研究](https://www.xbstack.com/ai/qwen-audio-live-voice-agent/?utm_source=github&utm_medium=referral&utm_campaign=qwen_audio_live_voice_agent&utm_content=problem_labs_repro)
- [Qwen-Audio-Live WebSocket access](https://www.alibabacloud.com/help/en/model-studio/qwen-audio-live-websocket-access)
- [Research paper](https://arxiv.org/abs/2609.25195)

The next validation steps are authenticated session binding, remote idempotency, reconnect/replay, and real audio testing in an authorized sandbox. This is an independent offline reference, not an official vendor SDK or reported vendor bug.
