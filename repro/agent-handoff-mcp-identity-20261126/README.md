# Agent handoff: MCP metadata precedence and transport credential separation

Test date: 2026-11-26. An independent XBSTACK lab, using synthetic record identifiers and dummy HTTP credentials only.

## Reproduce

From this directory:

```bash
python3 run_versions.py
python3 run_transport.py
```

The first runner downloads the official 0.25.0 and 0.26.0 PyPI wheels, verifies SHA-256 and runs only the original metadata-merge method extracted from each wheel. The second creates an isolated temporary venv, installs pinned Agents SDK 0.26.0, MCP SDK 2.3.0 and uvicorn 0.52.1, and runs the real SDK's ScriptedModel through an ephemeral loopback HTTP server. The venv is removed automatically. Python 3.11 is recommended for the transport runner; no paid model API, API key or external MCP server is used. Installing packages requires network access to PyPI.

## Observations

| Case | Observation |
| --- | --- |
| 0.25.0 discovery collision | Discovered default wins |
| 0.26.0 discovery collision | Per-call resolver wins |
| Explicit caller metadata | Wins on both versions |
| Non-conflicting keys, empty metadata, nested-copy isolation | All five assertions on each version pass |
| 0.26.0 shared MCP client object | Two real HTTP tool calls; actor labels change, credential hashes match |
| 0.26.0 separate MCP client objects | Two real HTTP tool calls; actor labels change, credential hashes differ |

See [sdk-source-result.json](sdk-source-result.json) and [transport-result.json](transport-result.json) for the actual recorded **10/10 + 6/6** assertions, exact wheel digests and environment. The source-level experiment does not independently exercise the entire 0.25.0 runtime. The HTTP fixture deliberately has no OAuth issuer or signed identity validation. Different dummy headers do **not** establish verified actor identity, least privilege or production authorization.

## Application design

Authenticate at the resource server; do not treat model-generated parameters or an unsigned metadata actor label as authentication. Bind the verified user, acting agent, resource audience, tenant, scope and current policy to each tool call. Evaluate handoff permission before transfer and enforce the destination policy again before execution; separate connection objects alone are not a substitute for least-privilege credentials. Bind approval to the exact invocation, re-check policy and expiry on resume, and keep credential material out of model context and logs. Use a supported issuer and authorization library, not a home-grown token verifier.

## Original upstream sources

- [Agents SDK releases](https://github.com/openai/openai-agents-python/releases/tag/v0.26.0)
- [Merged metadata precedence change #6179](https://github.com/openai/openai-agents-python/pull/6179)
- [Handoff credential feature request #6215](https://github.com/openai/openai-agents-python/issues/6215)
- [MCP integration documentation](https://openai.github.io/openai-agents-python/mcp/)
- [MCP authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)

Related XBSTACK production security guide: [AI Agent Tool Authorization](https://www.xbstack.com/en/ai/ai-agent-tool-authorization-policy-gate/?utm_source=github&utm_medium=referral&utm_campaign=ai_agent_tool_authorization_policy_gate&utm_content=handoff_identity_lab). The guide explains the existing Policy Gate design; the new lab evidence is maintained here independently of the website's deployment schedule.
