# XBSTACK Problem Labs

**Reproducible AI engineering failures, version matrices, workarounds, and upstream evidence.**

This repository is the GitHub-native index for XBSTACK debugging labs. Each entry starts from a real developer problem and links the shortest useful path:

**error / symptom → minimal reproduction → affected versions → tested containment → upstream issue → full XBSTACK analysis**

> Website index: https://www.xbstack.com/github/?utm_source=github&utm_medium=referral&utm_campaign=problem_labs&utm_content=repository_readme

## LangGraph

| Problem | Reproduction | Upstream | Full analysis |
| --- | --- | --- | --- |
| `aupdate_state` raises `InvalidUpdateError: Ambiguous update, specify as_node` while sync `update_state` succeeds | [langgraph-aupdate-state-ambiguous-update-repro](https://github.com/xbstack/langgraph-aupdate-state-ambiguous-update-repro) | [langgraph#8714](https://github.com/langchain-ai/langgraph/issues/8714) | [XBSTACK](https://www.xbstack.com/en/ai/langgraph-aupdate-state-ambiguous-update/?utm_source=github&utm_medium=referral&utm_campaign=langgraph_aupdate_state_ambiguous_update&utm_content=problem_labs) |
| ToolNode async execution ignores `RunnableConfig.max_concurrency` | [langgraph-toolnode-max-concurrency-repro](https://github.com/xbstack/langgraph-toolnode-max-concurrency-repro) | [langgraph#8517](https://github.com/langchain-ai/langgraph/issues/8517) | [XBSTACK](https://www.xbstack.com/en/ai/langgraph-toolnode-max-concurrency-ignored/?utm_source=github&utm_medium=referral&utm_campaign=langgraph_toolnode_max_concurrency&utm_content=problem_labs) |
| SQLite store batch failure can partially commit an earlier TTL mutation | [langgraph-sqlite-partial-commit-repro](https://github.com/xbstack/langgraph-sqlite-partial-commit-repro) | [langgraph#8590](https://github.com/langchain-ai/langgraph/issues/8590) | [XBSTACK](https://www.xbstack.com/en/ai/langgraph-checkpointer-memory-sqlite-redis/?utm_source=github&utm_medium=referral&utm_campaign=langgraph_sqlite_partial_commit&utm_content=problem_labs) |

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

| Problem | Tool / reproduction | Full analysis |
| --- | --- | --- |
| MCP stdio `-32700 Parse Error`, polluted stdout, or tool-list failure | [mcp-stdio-diagnostics](https://github.com/xbstack/mcp-stdio-diagnostics) | [XBSTACK](https://www.xbstack.com/en/ai/mcp-json-rpc-parse-error/?utm_source=github&utm_medium=referral&utm_campaign=mcp_parse_error_fix&utm_content=problem_labs) |

## AI SDK

| Problem | Reproduction | Full analysis |
| --- | --- | --- |
| AI SDK 7 migration: tool calls, streaming, interruption and recovery boundaries | [xbstack-ai-sdk-7-migration-demo](https://github.com/xbstack/xbstack-ai-sdk-7-migration-demo) | [XBSTACK](https://www.xbstack.com/en/ai/vercel-ai-sdk-7-migration-production/?utm_source=github&utm_medium=referral&utm_campaign=ai_sdk_7_migration&utm_content=problem_labs) |

## How these labs are maintained

- Reproduction evidence is separated from inference and vendor claims.
- A workaround is labeled as a workaround until an upstream fix is verified.
- Version matrices are rerun when a candidate fixed release appears.
- GitHub Issue/Discussion replies include a site link only when the linked XBSTACK page directly addresses the thread's problem.
- No generic promotional replies, unrelated backlinks, or copied article dumps.

## Search terms covered

LangGraph `aupdate_state` Ambiguous update · LangGraph max_concurrency ignored · LangGraph SQLite partial commit · n8n `$json` Array null · n8n Raw Body stream · n8n ARM64 GLIBC_PRIVATE · OpenAI Responses No tool call found · OpenAI Agents RunState approval resume · MCP -32700 Parse Error · AI SDK 7 migration
