# Pydantic Pax / Harness evidence (2026-11-27)

Independent XBSTACK engineering research, not a vendor benchmark or certification.

- Official release: https://pydantic.dev/articles/pax-harness-beta
- [Full research (EN)](https://www.xbstack.com/en/ai/tools-lab/pydantic-pax-coding-agent-harness/?utm_source=github&utm_medium=referral&utm_campaign=pydantic_pax_coding_agent_harness&utm_content=lab_readme)
- [中文研究](https://www.xbstack.com/ai/tools-lab/pydantic-pax-coding-agent-harness/?utm_source=github&utm_medium=referral&utm_campaign=pydantic_pax_coding_agent_harness&utm_content=lab_readme)

## Evidence and limits

- `audit.py` and `result.json`: original pinned PyPI wheel AST inspection and arithmetic on the vendor's published SWE81 aggregate cells. 12 checks passed. It does not reproduce the vendor's SWE81 run.
- `runtime_probe.py`, `isolated_runner.py`, `runtime-result.json`: original offline experiment. Pydantic AI Pax 0.75.0, Harness 0.75.0, Pydantic AI Slim 2.75.0; exact observed versions in the JSON. Historical machine Apple M1 Pro, 10 CPU cores, 16 GiB, Python 3.11.15. 60 timed trials plus warmups; no hosted model calls. The scripted FunctionModel injects delay per simulated model request, not per tool call. Median total elapsed time for the ten-step chain: native/code 15.37/25.43 ms at 0 ms, 365.35/92.10 ms at 25 ms, 1211.23/270.52 ms at 100 ms. These are synthetic local measurements, not commercial-model quality, price, security, production readiness or Pax-versus-Codex latency claims.

## Reproduction

Keep the original JSON files unchanged in the Git revision. Run `python3 audit.py` in a disposable copy with network access to PyPI. It verifies three wheel SHA-256 digests and parses sources without importing downloaded code. For the runtime fixture use a separate disposable macOS test environment with Python 3.11, uv at ~/.local/bin/uv and sandbox-exec available. Review the historical runner before running it: the installation phase uses network access, while runtime denies network and user home reads; the historical machine label is fixed to the original test machine and must not be reused as a claim for another machine. Dependency transitives are not fully locked; inspect observed versions and compare the qualitative call-count assertions rather than expect identical timings. Run `python3 isolated_runner.py` only in an environment matching those constraints. Do not provide provider keys or production data. Re-running writes new JSON files in the disposable copy. Do not treat the sandbox probe as a security certification.

The five original experiment files are preserved byte-for-byte. No paid Actions are configured or required.
