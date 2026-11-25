"""Offline SQLite reference: durable local intent and result outbox, not a vendor SDK."""
import sqlite3
import tempfile
import unittest
import json
import platform
from pathlib import Path

class Ledger:
    def __init__(self, path):
        self.db = sqlite3.connect(path, timeout=5)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS task (
          owner TEXT, session TEXT, delegation TEXT, state TEXT NOT NULL,
          PRIMARY KEY(owner,session,delegation)
        );
        CREATE TABLE IF NOT EXISTS outbox (
          owner TEXT, session TEXT, delegation TEXT, result TEXT NOT NULL,
          acked INTEGER NOT NULL DEFAULT 0,
          PRIMARY KEY(owner,session,delegation),
          FOREIGN KEY(owner,session,delegation) REFERENCES task(owner,session,delegation)
        );
        """)

    def close(self): self.db.close()
    def accept(self, key, operation):
        if operation != "synthetic_lookup": return False
        with self.db:
            return self.db.execute("INSERT OR IGNORE INTO task VALUES (?,?,?,'pending')", key).rowcount == 1

    def cancel(self, key):
        with self.db:
            return self.db.execute("UPDATE task SET state='cancelled' WHERE owner=? AND session=? AND delegation=? AND state='pending'",key).rowcount == 1

    def finish(self, key, result, simulate_failure=False):
        with self.db:
            changed = self.db.execute("UPDATE task SET state='completed' WHERE owner=? AND session=? AND delegation=? AND state='pending'",key).rowcount
            if not changed: return False
            if simulate_failure: raise RuntimeError("synthetic interruption before outbox insert")
            self.db.execute("INSERT INTO outbox(owner,session,delegation,result) VALUES (?,?,?,?)", (*key,result))
            return True

    def pending(self, owner, session):
        return self.db.execute("SELECT delegation,result FROM outbox WHERE owner=? AND session=? AND acked=0 ORDER BY delegation",(owner,session)).fetchall()

    def ack(self, key):
        with self.db:
            return self.db.execute("UPDATE outbox SET acked=1 WHERE owner=? AND session=? AND delegation=? AND acked=0",key).rowcount == 1

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(self.temp.name)/"tasks.sqlite"
        self.a=Ledger(self.path)
        self.key=("owner-a","session-a","task-1")
    def tearDown(self):
        self.a.close()
        self.temp.cleanup()
    def reopen(self):
        self.a.close()
        self.a=Ledger(self.path)
    def test_reopen_duplicate(self):
        self.assertTrue(self.a.accept(self.key,"synthetic_lookup"))
        self.reopen()
        self.assertFalse(self.a.accept(self.key,"synthetic_lookup"))
        self.assertTrue(self.a.finish(self.key,"result"))
        self.reopen()
        self.assertFalse(self.a.finish(self.key,"duplicate"))
        self.assertEqual(self.a.pending(*self.key[:2]),[("task-1","result")])
    def test_atomic_result_outbox(self):
        self.a.accept(self.key,"synthetic_lookup")
        with self.assertRaises(RuntimeError): self.a.finish(self.key,"bad",True)
        self.reopen()
        self.assertEqual(self.a.pending(*self.key[:2]),[])
        self.assertTrue(self.a.finish(self.key,"ok"))
        self.assertEqual(self.a.pending(*self.key[:2]),[("task-1","ok")])
    def test_ack_and_replay(self):
        self.a.accept(self.key,"synthetic_lookup")
        self.a.finish(self.key,"ok")
        first=self.a.pending(*self.key[:2])
        self.reopen()
        self.assertEqual(self.a.pending(*self.key[:2]),first)
        self.assertTrue(self.a.ack(self.key))
        self.reopen()
        self.assertEqual(self.a.pending(*self.key[:2]),[])
        self.assertFalse(self.a.ack(self.key))
    def test_cancel_persists(self):
        self.a.accept(self.key,"synthetic_lookup")
        self.assertTrue(self.a.cancel(self.key))
        self.reopen()
        self.assertFalse(self.a.finish(self.key,"late"))
        self.assertEqual(self.a.pending(*self.key[:2]),[])
    def test_scope_and_allowlist(self):
        self.assertFalse(self.a.accept(self.key,"delete_document"))
        self.a.accept(self.key,"synthetic_lookup")
        wrong=("owner-b","session-a","task-1")
        self.assertFalse(self.a.cancel(wrong))
        self.assertFalse(self.a.finish(wrong,"bad"))
        self.assertTrue(self.a.finish(self.key,"ok"))
        self.assertEqual(self.a.pending(*wrong[:2]),[])
        self.assertFalse(self.a.ack(wrong))
    def test_two_connections(self):
        self.a.accept(self.key,"synthetic_lookup")
        other=Ledger(self.path)
        try:
            self.assertTrue(other.finish(self.key,"first"))
            self.assertFalse(self.a.finish(self.key,"second"))
            self.assertEqual(self.a.pending(*self.key[:2]),[("task-1","first")])
        finally: other.close()

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={"scope":"SQLite local synthetic ledger; close/reopen and exception rollback, not process-kill or external effects","platform":platform.system(),"python":platform.python_version(),"sqlite":sqlite3.sqlite_version,"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"passed":result.wasSuccessful(),"vendor_calls":0,"audio":False,"exactly_once_network_delivery_verified":False}
    Path(__file__).with_name("durable-result.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report))
    raise SystemExit(0 if result.wasSuccessful() else 1)
