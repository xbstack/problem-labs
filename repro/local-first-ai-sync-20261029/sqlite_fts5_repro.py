#!/usr/bin/env python3
"""XBSTACK synthetic local-first sync + FTS5 fixture. Not an OwnRAG product test.

Trusted revisions are deliberately assumed; concurrency/CRDT and encryption are OUT OF SCOPE.
The FTS5 index is derived on each replica and is never present in the sync payload.
"""
import json
import sqlite3
import unittest


class Replica:
    def __init__(self, label):
        self.label = label
        self.db = sqlite3.connect(":memory:")
        self.db.executescript("""
        CREATE TABLE source (
            id TEXT PRIMARY KEY,
            revision INTEGER NOT NULL,
            body TEXT NOT NULL,
            deleted INTEGER NOT NULL DEFAULT 0
        );
        CREATE VIRTUAL TABLE fts USING fts5(body, content='source', content_rowid='rowid');
        CREATE TRIGGER source_ai AFTER INSERT ON source WHEN new.deleted = 0 BEGIN
            INSERT INTO fts(rowid,body) VALUES(new.rowid,new.body);
        END;
        CREATE TRIGGER source_au AFTER UPDATE ON source BEGIN
            INSERT INTO fts(fts,rowid,body) SELECT 'delete',old.rowid,old.body WHERE old.deleted = 0;
            INSERT INTO fts(rowid,body) SELECT new.rowid,new.body WHERE new.deleted = 0;
        END;
        CREATE TRIGGER source_ad AFTER DELETE ON source WHEN old.deleted = 0 BEGIN
            INSERT INTO fts(fts,rowid,body) VALUES('delete',old.rowid,old.body);
        END;
        """)

    def apply(self, event):
        ident, rev, body, deleted = (
            event["id"], event["revision"], event["body"], int(event["deleted"])
        )
        current = self.db.execute(
            "SELECT revision,deleted FROM source WHERE id=?", (ident,)
        ).fetchone()
        if current:
            oldrev, olddeleted = current
            if rev < oldrev or (rev == oldrev and (olddeleted or not deleted)):
                return False
            self.db.execute(
                "UPDATE source SET revision=?,body=?,deleted=? WHERE id=?",
                (rev, body, deleted, ident),
            )
        else:
            self.db.execute(
                "INSERT INTO source(id,revision,body,deleted) VALUES(?,?,?,?)",
                (ident, rev, body, deleted),
            )
        self.db.commit()
        return True

    def payload(self):
        return [
            dict(id=row[0], revision=row[1], body=row[2], deleted=bool(row[3]))
            for row in self.db.execute("SELECT id,revision,body,deleted FROM source")
        ]

    def receive(self, events):
        for event in events:
            self.apply(event)

    def search(self, term):
        return [
            row[0]
            for row in self.db.execute(
                """SELECT source.id FROM fts
                JOIN source ON source.rowid = fts.rowid
                WHERE fts MATCH ? AND source.deleted=0
                ORDER BY source.id""",
                (term,),
            )
        ]


def make(ident, revision, body, deleted=False):
    return dict(id=ident, revision=revision, body=body, deleted=deleted)


class SyntheticSyncFTS5Test(unittest.TestCase):
    def test_sync_payload_excludes_index(self):
        a, b = Replica("phone"), Replica("desktop")
        a.apply(make("doc", 1, "orchid glacier"))
        payload = a.payload()
        self.assertEqual(set(payload[0]), {"id", "revision", "body", "deleted"})
        b.receive(payload)
        self.assertEqual(b.search("orchid"), ["doc"])

    def test_index_rebuilds_on_source_update(self):
        b = Replica("desktop")
        b.apply(make("doc", 1, "orchid glacier"))
        b.apply(make("doc", 2, "cedar glacier"))
        self.assertEqual(b.search("orchid"), [])
        self.assertEqual(b.search("cedar"), ["doc"])

    def test_tombstone_sync_clears_live_search(self):
        a, b = Replica("phone"), Replica("desktop")
        a.apply(make("doc", 1, "orchid glacier"))
        b.receive(a.payload())
        a.apply(make("doc", 3, "", deleted=True))
        b.receive(a.payload())
        self.assertEqual(a.search("orchid"), [])
        self.assertEqual(b.search("orchid"), [])

    def test_stale_replay_cannot_resurrect(self):
        b = Replica("desktop")
        b.apply(make("doc", 3, "", deleted=True))
        self.assertFalse(b.apply(make("doc", 2, "orchid glacier")))
        self.assertEqual(b.search("orchid"), [])

    def test_delete_does_not_touch_other_documents(self):
        b = Replica("desktop")
        b.apply(make("x", 1, "orchid alpine"))
        b.apply(make("y", 1, "orchid coastal"))
        b.apply(make("x", 2, "", deleted=True))
        self.assertEqual(b.search("orchid"), ["y"])

    def test_offline_replica_remains_stale_until_delivery(self):
        a, b = Replica("phone"), Replica("offline")
        a.apply(make("x", 1, "orchid alpine"))
        b.receive(a.payload())
        a.apply(make("x", 2, "", deleted=True))
        self.assertEqual(b.search("orchid"), ["x"])
        b.receive(a.payload())
        self.assertEqual(b.search("orchid"), [])

    def test_fts_rebuild_from_current_source(self):
        a = Replica("phone")
        a.apply(make("x", 1, "orchid alpine"))
        a.apply(make("x", 2, "", deleted=True))
        a.apply(make("y", 1, "orchid coastal"))
        a.db.execute("INSERT INTO fts(fts) VALUES('rebuild')")
        self.assertEqual(a.search("orchid"), ["y"])

    def test_same_revision_delete_wins_fixture(self):
        b = Replica("desktop")
        b.apply(make("x", 2, "orchid alpine"))
        b.apply(make("x", 2, "", deleted=True))
        self.assertFalse(b.apply(make("x", 2, "orchid alpine")))
        self.assertEqual(b.search("orchid"), [])


if __name__ == "__main__":
    print(json.dumps({"sqlite_version": sqlite3.sqlite_version, "database": ":memory:", "test_scope": "synthetic"}))
    unittest.main(verbosity=2)
