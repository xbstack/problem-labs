# Local-first AI knowledge sync: source revisions, FTS5 and tombstones

Original study: 2026-10-29. Independently rerun 2026-11-26 before publishing this fixture.

## Reproduce

```sh
node --test repro.mjs
python3 sqlite_fts5_repro.py
```

Node.js with the built-in test runner; Python 3 with SQLite compiled with FTS5. No dependencies, API calls, model downloads or real user data.

- Node v22.18.0: **7/7** passing synthetic tests.
- Python 3.10.2, SQLite 3.35.5, in-memory database: **8/8** passing tests.
- [Recorded environment and source hashes](result.json); [raw test output](test-output.txt).

The fixtures assume trusted per-document monotonic revisions. They demonstrate that source records, rather than materialized indexes, are copied; changed sources rebuild the local index; delivered tombstones stop live search; stale replay cannot resurrect a tombstone; and an offline replica can still return old results before deletion arrives. In the SQLite case, the live query filters deleted rows. These cases overlap; they do not establish fifteen independent production guarantees.

## Explicit limitations

Not a production synchronization protocol, general concurrent CRDT, encryption implementation, real OwnRAG test, neural embedding benchmark, network reliability test, or evidence of physical erasure. No model or real documents are loaded. The Python public copy changes only the old product-name spelling in its docstring.

## Full research

- [English: architecture, conflict and citation verification](https://www.xbstack.com/en/ai/local-first-ai-knowledge-sync/?utm_source=github&utm_medium=referral&utm_campaign=local_first_ai_sync&utm_content=lab_readme)
- [中文：原文同步、向量索引、冲突和删除](https://www.xbstack.com/ai/local-first-ai-knowledge-sync/?utm_source=github&utm_medium=referral&utm_campaign=local_first_ai_sync&utm_content=lab_readme)
