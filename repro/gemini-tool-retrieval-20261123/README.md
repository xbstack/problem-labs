# Gemini Tool Retrieval: offline discovery-boundary fixture

Published 2026-11-25. This reproduces synthetic JSON payload shapes and an application-owned allowlist, not Gemini API behavior or a provider security certification.

## Run
```sh
cd repro/gemini-tool-retrieval-20261123
python3 -S compare.py
python3 -S -m unittest discover -s . -p 'test_*.py' -v
```

Actual local rerun on 2026-11-25: 4 tests passed. 64 synthetic function declarations; 3 permitted. Static full-schema JSON: 29,408 bytes; server-deferred initial JSON: 9,911 bytes; client-search initial JSON: 120 bytes; returned allowed schemas: 905 bytes. These are UTF-8 serialized bytes, NOT tokens, API costs or latency. The fixture checks that names/description headers remain present in the simulated server-deferred payload and that a client-owned search does not return denied tools. Execution still requires independent backend authorization.

No network, credentials, real private records, paid API calls or real model evaluation. Source: [Google's Tool Retrieval announcement](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-api-tool-retrieval/).

- [English engineering analysis](https://www.xbstack.com/en/ai/gemini-tool-retrieval-dynamic-mcp-tools/?utm_source=github&utm_medium=referral&utm_campaign=gemini_tool_retrieval_mcp&utm_content=problem_labs_repro)
- [中文工程分析](https://www.xbstack.com/ai/gemini-tool-retrieval-dynamic-mcp-tools/?utm_source=github&utm_medium=referral&utm_campaign=gemini_tool_retrieval_mcp&utm_content=problem_labs_repro)

License: repository MIT.
