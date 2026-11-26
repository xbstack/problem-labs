import assert from 'node:assert/strict';
import { test } from 'node:test';

const clone = (x) => JSON.parse(JSON.stringify(x));
class Device {
  constructor(name) { this.name = name; this.sources = new Map(); this.localIndex = new Map(); }
  // This fixture assumes a trusted source assigns monotonically increasing
  // per-document revisions. It is NOT a general concurrent CRDT algorithm.
  apply(change) {
    const prev = this.sources.get(change.id);
    if (prev && change.revision < prev.revision) return false;
    if (prev && change.revision === prev.revision) {
      if (prev.deleted) return false; // a tombstone cannot be overwritten by same-revision data
      if (!change.deleted) return false;
    }
    this.sources.set(change.id, clone(change));
    this.localIndex.delete(change.id);
    if (!change.deleted) this.localIndex.set(change.id, {revision:change.revision, keywords:change.text.toLowerCase().split(/\s+/)});
    return true;
  }
  exportChanges() { return [...this.sources.values()].map(clone); }
  receive(changes) { for (const c of changes) this.apply(c); }
  find(word) { return [...this.localIndex].filter(([id,ix]) => ix.keywords.includes(word.toLowerCase()) && !this.sources.get(id)?.deleted).map(([id])=>id); }
}
const doc = (id, revision, text, deleted=false)=>({id,revision, text, deleted});

test('sync transfers sources, not local indexes',()=>{
 const a=new Device('a'); a.apply(doc('1',1,'private note'));
 const payload=a.exportChanges(); assert.equal('keywords' in payload[0],false);
 const b=new Device('b'); b.receive(payload);assert.deepEqual(b.find('private'),['1']);
});
test('receiving changed source invalidates and rebuilds local index',()=>{
 const b=new Device('b');b.receive([doc('1',1,'red note')]);b.receive([doc('1',2,'blue note')]);
 assert.deepEqual(b.find('red'),[]);assert.deepEqual(b.find('blue'),['1']);
});
test('tombstone removes source from both retrieval indexes after delivery',()=>{
 const a=new Device('a'),b=new Device('b');a.apply(doc('1',1,'secret note'));b.receive(a.exportChanges());
 a.apply(doc('1',3,'',true));b.receive(a.exportChanges());
 assert.deepEqual(a.find('secret'),[]);assert.deepEqual(b.find('secret'),[]);
});
test('old replay cannot resurrect a tombstoned document',()=>{
 const d=new Device('d');d.apply(doc('1',3,'',true));d.receive([doc('1',2,'secret note')]);
 assert.deepEqual(d.find('secret'),[]);assert.equal(d.sources.get('1').deleted,true);
});
test('deletion remains scoped to document and preserves other sources',()=>{
 const d=new Device('d');d.receive([doc('a',1,'a note'),doc('b',1,'b note')]);d.apply(doc('a',2,'',true));
 assert.deepEqual(d.find('b'),['b']);
});
test('offline replica is stale until it receives deletion',()=>{
 const a=new Device('a'),b=new Device('b');a.apply(doc('1',1,'secret'));b.receive(a.exportChanges());a.apply(doc('1',2,'',true));
 assert.deepEqual(b.find('secret'),['1']); // security limit: no remote guarantee while offline
 b.receive(a.exportChanges());assert.deepEqual(b.find('secret'),[]);
});
test('same-revision tombstone wins over data in this fixture',()=>{
 const d=new Device('d');d.apply(doc('1',2,'text'));d.apply(doc('1',2,'',true));
 d.receive([doc('1',2,'text')]);assert.equal(d.sources.get('1').deleted,true);
});
