# XBSTACK Problem Labs

**Reproducible AI engineering failures, version matrices, workarounds, and upstream evidence.**

This repository is the GitHub-native index for XBSTACK debugging labs. Each entry starts from a real developer problem and links the shortest useful path:

**error / symptom → minimal reproduction → affected versions → tested containment → upstream issue → full XBSTACK analysis**

> Website index: https://www.xbstack.com/github/?utm_source=github&utm_medium=referral&utm_campaign=problem_labs&utm_content=repository_readme

## Interactive voice agents (2026-11-25)

- [Offline asynchronous task and SQLite outbox lab](repro/voice-agent-async-task-20261125/README.md): 12/12 local synthetic tests, cancellation, session scoping, durable intent and acknowledgment. No vendor API, audio or exactly-once network delivery claim.
- [XBSTACK architecture analysis](https://www.xbstack.com/en/ai/qwen-audio-live-voice-agent/?utm_source=github&utm_medium=referral&utm_campaign=qwen_audio_live_voice_agent&utm_content=problem_labs_readme).

## Gemini / MCP tool discovery (2026-11-25)

- [Gemini Tool Retrieval offline fixture](repro/gemini-tool-retrieval-20261123/README.md): 64 synthetic tool declarations, 3 permitted tools, 4/4 local tests. Compares serialized JSON bytes and application authorization boundaries, **not** model tokens, latency, billing or actual API performance.
- [XBSTACK engineering analysis](https://www.xbstack.com/en/ai/gemini-tool-retrieval-dynamic-mcp-tools/?utm_source=github&utm_medium=referral&utm_campaign=gemini_tool_retrieval_mcp&utm_content=problem_labs_readme).

## Supply-chain security: Microsoft Agent Framework PyPI compromise (2026-11-17)

- [Read-only offline scanner and **3/3 passing synthetic tests**](repro/agent-framework-pypi-20261123/README.md) for official PyPI `agent-framework` **1.26.1/1.26.2**, both `.pth` startup-hook names, wheel metadata, copied `site-packages` and pinned requirements/lock references.
- [GHSA-764m-3ppc-5m73](https://github.com/advisories/GHSA-764m-3ppc-5m73). **Safe boundary:** the scanner does not import, install, execute or fetch a malicious wheel or touch credential material. Synthetic indicators are not proof of actual exfiltration; absence of matches cannot certify a machine that may have run the compromised package. In an affected environment, investigate from a trusted host and rotate potentially exposed secrets.
- [Related Agent security guidance](https://www.xbstack.com/en/ai/ai-agent-security/?utm_source=github&utm_medium=referral&utm_campaign=agent_framework_pypi_20261123&utm_content=problem_labs_repro).

## LangGraph

| Problem | Reproduction | Upstream | Full analysis |
| --- | --- | --- | --- |
| `aupdate_state` raises `InvalidUpdateError: Ambiguous update, specify as_node` while sync `update_state` succeeds | [langgraph-aupdate-state-ambiguous-update-repro](https://github.com/xbstack/langgraph-aupdate-state-ambiguous-update-repro) | [langgraph#8714](https://github.com/langchain-ai/langgraph/issues/8714) | [XBSTACK](https://www.xbstack.com/en/ai/langgraph-aupdate-state-ambiguous-update/?utm_source=github&utm_medium=referral&utm_campaign=langgraph_aupdate_state_ambiguous_update&utm_content=problem_labs) |
| `Command(resume=dict)` can mistake ordinary dict values for targeted interrupt maps | [langgraph-command-resume-dict-misclassification-repro](https://github.com/xbstack/langgraph-command-resume-dict-misclassification-repro) | [langgraph#8693](https://github.com/langchain-ai/langgraph/issues/8693) | [compatibility tracker](https://www.xbstack.com/en/tools/mcp-radar/?utm_source=github&utm_medium=referral&utm_campaign=langgraph_resume_dict_8693&utm_content=problem_labs) |
| ToolNode async execution ignores `RunnableConfig.max_concurrency` | [langgraph-toolnode-max-concurrency-repro](https://github.com/xbstack/langgraph-toolnode-max-concurrency-repro) | [langgraph#8517](https://github.com/langchain-ai/langgraph/issues/8517) | [XBSTACK](https://www.xbstack.com/en/ai/langgraph-toolnode-max-concurrency-ignored/?utm_source=github&utm_medium=referral&utm_campaign=langgraph_toolnode_max_concurrency&utm_content=problem_labs) |
| SQLite store batch failure can partially commit an earlier TTL mutation | [langgraph-sqlite-partial-commit-repro](https://github.com/xbstack/langgraph-sqlite-partial-commit-repro) | [langgraph#8590](https://github.com/langchain-ai/langgraph/issues/8590) | [XBSTACK](https://www.xbstack.com/en/ai/langgraph-checkpointer-memory-sqlite-redis/?utm_source=github&utm_medium=referral&utm_campaign=langgraph_sqlite_partial_commit&utm_content=problem_labs) |
| Accepted run can disappear if the process dies before the first durable checkpoint; fresh-process resume then raises `EmptyInputError` | [langgraph-first-checkpoint-acceptance-ledger-repro](https://github.com/xbstack/langgraph-first-checkpoint-acceptance-ledger-repro) | [langgraph#8764](https://github.com/langchain-ai/langgraph/issues/8764) | [XBSTACK lab index](https://www.xbstack.com/github/?utm_source=github&utm_medium=referral&utm_campaign=langgraph_first_checkpoint_acceptance_ledger&utm_content=problem_labs&ref=github) |

## n8n

| Problem | Reproduction | Upstream | Full analysis |
| --- | --- | --- | --- |
| n8n 2.35.3: mutating Array methods on `$json` return `null` | [n8n-2353-json-array-null-repro](https://github.com/xbstack/n8n-2353-json-array-null-repro) | [n8n#36540](https://github.com/n8n-io/n8n/issues/36540) | [XBSTACK](https://www.xbstack.com/en/ai/n8n-2353-json-array-methods-return-null/?utm_source=github&utm_medium=referral&utm_campaign=n8n_2353_array_null_regression&utm_content=problem_labs) |
| HTTP Request Raw body + explicit JSON response returns stream internals | [n8n-http-request-raw-body-stream-repro](https://github.com/xbstack/n8n-http-request-raw-body-stream-repro) | [n8n#36402](https://github.com/n8n-io/n8n/issues/36402) | [XBSTACK](https://www.xbstack.com/en/ai/n8n-http-request-raw-body-response-stream/?utm_source=github&utm_medium=referral&utm_campaign=n8n_http_raw_response_stream&utm_content=problem_labs) |
| ARM64 distroless task runner fails with GLIBC / `GLIBC_PRIVATE` mismatch | [n8n-distroless-arm64-glibc-repro](https://github.com/xbstack/n8n-distroless-arm64-glibc-repro) | [n8n#35913](https://github.com/n8n-io/n8n/issues/35913) | [XBSTACK](https://www.xbstack.com/en/ai/n8n-distroless-arm64-glibc-error/?utm_source=github&utm_medium=referral&utm_campaign=n8n_distroless_arm64_glibc&utm_content=problem_labs) |

## OpenAI

| Problem | Reproduction / lab | Upstream | Full analysis |
| --- | --- | --- | --- |
| Responses API stream abort can leave a later `function_call_output` with `No tool call found` | [openai-responses-stream-abort-tool-call-loss](https://github.com/xbstack/openai-responses-stream-abort-tool-call-loss) | [openai-python#3561](https://github.com/openai/openai-python/issues/3561) | [XBSTACK](https://www.xbstack.com/en/ai/openai-responses-api-stream-abort-tool-call-lost/?utm_source=github&utm_medium=referral&utm_campaign=openai_responses_stream_abort&utm_content=problem_labs) |
| Agents SDK RunState approval/resume across processes, redelivery and idempotency | [openai-agents-runstate-approval-resume-lab](https://github.com/xbstack/openai-agents-runstate-approval-resume-lab) | [v0.19.3 / PR #4126](https://github.com/openai/openai-agents-python/pull/4126) | [XBSTACK](https://www.xbstack.com/en/ai/openai-agents-sdk-runstate-approval-resume/?utm_source=github&utm_medium=referral&utm_campaign=openai_agents_runstate&utm_content=problem_labs) |

## MCP

| Problem | Tool / reproduction | Upstream | Full analysis |
| --- | --- | --- | --- |
| `StreamableHTTPClientTransport` POST stays pending after request-scoped SSE error / EOF until timeout | [mcp-streamable-http-sse-pending-repro](https://github.com/xbstack/mcp-streamable-http-sse-pending-repro) | [typescript-sdk#2739](https://github.com/modelcontextprotocol/typescript-sdk/issues/2739) | [XBSTACK](https://www.xbstack.com/en/ai/mcp-streamable-http-sse-pending-timeout/?utm_source=github&utm_medium=referral&utm_campaign=mcp_streamable_http_sse_pending&utm_content=problem_labs) |
| MCP stdio `-32700 Parse Error`, polluted stdout, or tool-list failure | [mcp-stdio-diagnostics](https://github.com/xbstack/mcp-stdio-diagnostics) | — | [XBSTACK](https://www.xbstack.com/en/ai/mcp-json-rpc-parse-error/?utm_source=github&utm_medium=referral&utm_campaign=mcp_parse_error_fix&utm_content=problem_labs) |

## AI SDK

| Problem | Reproduction | Full analysis |
| --- | --- | --- |
| AI SDK 7 migration: tool calls, streaming, interruption and recovery boundaries | [xbstack-ai-sdk-7-migration-demo](https://github.com/xbstack/xbstack-ai-sdk-7-migration-demo) | [XBSTACK](https://www.xbstack.com/en/ai/vercel-ai-sdk-7-migration-production/?utm_source=github&utm_medium=referral&utm_campaign=ai_sdk_7_migration&utm_content=problem_labs) |
| `WorkflowAgent` signed approval: unsupported baseline → opt-in signed replay enforcement | [ai-sdk-workflowagent-signed-approval-repro](https://github.com/xbstack/ai-sdk-workflowagent-signed-approval-repro) | [vercel/ai#19964](https://github.com/vercel/ai/issues/19964) · [PR #19976](https://github.com/vercel/ai/pull/19976) |

## Upstream issue watch (2026-11-06; not independently reproduced)

These upstream reports are **not XBSTACK reproductions**. Each link below points to an existing, reviewed technical guide. A closed issue does not by itself verify which release contains a fix; do not treat different root causes as interchangeable.

| Upstream report | Engineering check | Existing guide |
| --- | --- | --- |
| LangGraph [#9602](https://github.com/langchain-ai/langgraph/issues/9602) | Subgraph output schema + reducer under astream_events | [XBSTACK guide](https://www.xbstack.com/en/ai/langgraph-subgraph-worker-state/?utm_source=github&utm_medium=referral&utm_campaign=upstream_issue_watch_20261106&utm_content=problem_labs_readme) |
| LangGraph [#9556](https://github.com/langchain-ai/langgraph/issues/9556) | Parallel ToolNode Command.update message ordering (distinct from concurrency limits) | [XBSTACK guide](https://www.xbstack.com/en/ai/langgraph-toolnode-max-concurrency-ignored/?utm_source=github&utm_medium=referral&utm_campaign=upstream_issue_watch_20261106&utm_content=problem_labs_readme) |
| LangGraph [#9607](https://github.com/langchain-ai/langgraph/issues/9607) | SQLite Store integer filtering, distinct from checkpoint recovery | [XBSTACK guide](https://www.xbstack.com/en/ai/langgraph-checkpointer-memory-sqlite-redis/?utm_source=github&utm_medium=referral&utm_campaign=upstream_issue_watch_20261106&utm_content=problem_labs_readme) |
| LangGraph [#9546](https://github.com/langchain-ai/langgraph/issues/9546) | Stale dependent task output after crash recovery | [XBSTACK guide](https://www.xbstack.com/en/ai/langgraph-agent-error-recovery-retry-timeout/?utm_source=github&utm_medium=referral&utm_campaign=upstream_issue_watch_20261106&utm_content=problem_labs_readme) |
| n8n [#43032](https://github.com/n8n-io/n8n/issues/43032) | MCP failed-execution stack/result data minimization | [XBSTACK guide](https://www.xbstack.com/en/ai/mcp-security-best-practices/?utm_source=github&utm_medium=referral&utm_campaign=upstream_issue_watch_20261106&utm_content=problem_labs_readme) |
| n8n [#42981](https://github.com/n8n-io/n8n/issues/42981) | Regular-mode concurrency and stale workflow static data | [XBSTACK guide](https://www.xbstack.com/en/ai/self-hosted-n8n-ai-workflows/?utm_source=github&utm_medium=referral&utm_campaign=upstream_issue_watch_20261106&utm_content=problem_labs_readme) |
| Google ADK [#7987](https://github.com/google/adk-python/issues/7987) / [#7968](https://github.com/google/adk-python/issues/7968) | Human approval must be enforced; redirects require ongoing network gate | [XBSTACK guide](https://www.xbstack.com/en/ai/ai-agent-tool-authorization-policy-gate/?utm_source=github&utm_medium=referral&utm_campaign=upstream_issue_watch_20261106&utm_content=problem_labs_readme) |
| Google ADK [#7956](https://github.com/google/adk-python/issues/7956) / [#7977](https://github.com/google/adk-python/issues/7977) | CJK extraction and LiteLLM Gemma 4 role compatibility; issues closed, fix release not independently verified | [XBSTACK guide](https://www.xbstack.com/en/ai/ai-agent-framework-comparison/?utm_source=github&utm_medium=referral&utm_campaign=upstream_issue_watch_20261106&utm_content=problem_labs_readme) |

Do not post promotional issue comments. Contribute a minimal reproduction or version matrix only after independently verifying it.

## How these labs are maintained

- Reproduction evidence is separated from inference and vendor claims.
- A workaround is labeled as a workaround until an upstream fix is verified.
- Version matrices are rerun when a candidate fixed release appears.
- GitHub Issue/Discussion replies include a site link only when the linked XBSTACK page directly addresses the thread's problem.
- No generic promotional replies, unrelated backlinks, or copied article dumps.

## Search terms covered

LangGraph `aupdate_state` Ambiguous update · LangGraph `Command(resume=dict)` interrupt-map misclassification · LangGraph max_concurrency ignored · LangGraph SQLite partial commit · LangGraph first durable checkpoint · accepted run lost · `EmptyInputError` recovery · n8n `$json` Array null · n8n Raw Body stream · n8n ARM64 GLIBC_PRIVATE · OpenAI Responses No tool call found · OpenAI Agents RunState approval resume · MCP StreamableHTTPClientTransport SSE pending timeout · MCP -32700 Parse Error · AI SDK WorkflowAgent signed approval · AI SDK 7 migration
