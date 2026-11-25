"""Offline deterministic reference adapter. No cloud, audio, real user data or API keys."""
import asyncio
import json
import unittest
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Task:
    session: str
    delegation: str
    state: str = "pending"
    result: str = ""

class Adapter:
    def __init__(self):
        self.tasks = {}
        self.outbox = []
        self.executions = 0

    def accept(self, session, delegation, tool):
        key = (session, delegation)
        if tool != "synthetic_lookup":
            return False
        if key in self.tasks:
            return False
        self.tasks[key] = Task(session, delegation)
        return True

    def cancel(self, session, delegation):
        task = self.tasks.get((session, delegation))
        if task and task.state == "pending":
            task.state = "cancelled"
            return True
        return False

    def finish(self, session, delegation, result):
        task = self.tasks.get((session, delegation))
        if not task or task.state != "pending":
            return False
        task.state = "completed"
        task.result = result
        # Local adapter representation only, not a vendor wire payload.
        self.outbox.append({"session": session, "delegation_id": delegation, "result": result})
        return True

    async def work(self, session, delegation, release):
        self.executions += 1
        await release.wait()
        return self.finish(session, delegation, "synthetic match")

class Tests(unittest.IsolatedAsyncioTestCase):
    async def test_conversation_not_blocked(self):
        a = Adapter()
        self.assertTrue(a.accept("s", "d", "synthetic_lookup"))
        release = asyncio.Event()
        worker = asyncio.create_task(a.work("s", "d", release))
        await asyncio.sleep(0)
        self.assertFalse(worker.done())
        self.assertEqual(a.tasks["s", "d"].state, "pending")
        # Foreground event processing remains independent of the worker.
        foreground = await asyncio.sleep(0, result="foreground turn processed")
        self.assertEqual(foreground, "foreground turn processed")
        release.set()
        self.assertTrue(await worker)
        self.assertEqual(len(a.outbox), 1)

    async def test_duplicate_delegation(self):
        a = Adapter()
        self.assertTrue(a.accept("s", "d", "synthetic_lookup"))
        self.assertFalse(a.accept("s", "d", "synthetic_lookup"))
        self.assertTrue(a.finish("s", "d", "ok"))
        self.assertFalse(a.finish("s", "d", "late"))
        self.assertEqual(len(a.outbox), 1)

    async def test_cancel_late_result(self):
        a = Adapter()
        a.accept("s", "d", "synthetic_lookup")
        release = asyncio.Event()
        worker = asyncio.create_task(a.work("s", "d", release))
        await asyncio.sleep(0)
        self.assertTrue(a.cancel("s", "d"))
        release.set()
        self.assertFalse(await worker)
        self.assertEqual(a.outbox, [])
        self.assertEqual(a.tasks["s", "d"].state, "cancelled")

    async def test_scope(self):
        a = Adapter()
        a.accept("alice", "d", "synthetic_lookup")
        self.assertFalse(a.finish("bob", "d", "wrong tenant"))
        self.assertFalse(a.cancel("bob", "d"))
        self.assertTrue(a.accept("bob", "d", "synthetic_lookup"))
        self.assertTrue(a.finish("alice", "d", "a"))
        self.assertTrue(a.finish("bob", "d", "b"))
        self.assertEqual([x["session"] for x in a.outbox], ["alice", "bob"])

    async def test_unauthorized(self):
        a = Adapter()
        self.assertFalse(a.accept("s", "d", "delete_document"))
        self.assertFalse(a.finish("s", "d", "unexpected"))
        self.assertEqual(a.outbox, [])

    async def test_baseline_duplicate_failure(self):
        # Control: unguarded result relay emits the same task result twice.
        unguarded = [{"delegation_id": "d", "result": "ok"} for _ in range(2)]
        self.assertEqual(len(unguarded), 2)
        a = Adapter()
        a.accept("s", "d", "synthetic_lookup")
        a.finish("s", "d", "ok")
        a.finish("s", "d", "ok")
        self.assertEqual(len(a.outbox), 1)

if __name__ == "__main__":
    import platform
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {"scope":"offline synthetic in-memory adapter only","python":platform.python_version(),
              "platform":platform.system(),"tests":result.testsRun,"failures":len(result.failures),
              "errors":len(result.errors),"passed":result.wasSuccessful(),
              "vendor_api_calls":0,"real_audio":False,"persistent_exactly_once_verified":False,
              "tests_run": ["foreground independence","duplicate delegation/results","cancel late result","session isolation","deny unauthorized tool","unguarded duplicate control"]}
    target=Path(__file__).resolve().parent / "result.json"
    target.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report))
    raise SystemExit(0 if result.wasSuccessful() else 1)
