import assert from "node:assert/strict";
import {mkdtempSync,readFileSync,writeFileSync,rmSync,renameSync,fsyncSync,openSync,closeSync} from "node:fs";
import {tmpdir} from "node:os";
import {join} from "node:path";
import {createHash} from "node:crypto";

// Independent synthetic model of a local journal and a non-idempotent remote
// service. No provider SDK, HTTP, API key, wallet or actual charge.
const dir=mkdtempSync(join(tmpdir(),"output-retry-lab-"));
const results=[];
const check=(name,fn)=>{fn();results.push({name,pass:true});};
const hash=x=>createHash("sha256").update(x).digest("hex");
const file=join(dir,"journal.json");
function persist(value){
  const tmp=file+".tmp";
  const fd=openSync(tmp,"w",0o600);
  try {writeFileSync(fd,JSON.stringify(value));fsyncSync(fd);} finally {closeSync(fd);}
  renameSync(tmp,file);
}
const load=()=>JSON.parse(readFileSync(file,"utf8"));
const fresh=()=>persist({job:"synthetic",digest:hash("original prompt"),state:"new",remoteId:null});
let remote=[];
function provider(loseResponse=false){
  const task={id:"mock-"+(remote.length+1)};remote.push(task);
  return loseResponse?'{"taskId":"'+task.id+'"':JSON.stringify({taskId:task.id});
}
function decode(raw){
  const v=JSON.parse(raw);
  if(!v||typeof v!=="object"||Array.isArray(v)||typeof v.taskId!=="string"||!v.taskId)throw Error("invalid task envelope");
  return v.taskId;
}
function submit(prompt,loseResponse=false){
  const j=load();
  if(j.digest!==hash(prompt))throw Error("payload mismatch");
  if(j.state==="known")return j.remoteId;
  if(j.state!=="new")throw Error("ambiguous; reconcile before any new request");
  persist({...j,state:"unknown"});
  const id=decode(provider(loseResponse));
  persist({...j,state:"known",remoteId:id});return id;
}
function reconcile(id){
  const j=load();
  if(j.state!=="unknown"||!remote.some(x=>x.id===id))throw Error("no verified remote match");
  persist({...j,state:"known",remoteId:id});
}
function validateScenes(raw,count){
  const v=JSON.parse(raw);
  if(!v||!Array.isArray(v.scenes)||v.scenes.length!==count||
    !v.scenes.every(s=>typeof s.narration==="string"&&s.narration.trim()&&typeof s.visualPrompt==="string"&&s.visualPrompt.trim()))throw Error("schema mismatch");
  if(v.script!==v.scenes.map(s=>s.narration).join("\n\n"))throw Error("semantic mismatch");
  return v;
}
try{
  check("synthetic V8 offset 3003",()=>{
    const p='{"script":"';const raw=p+"x".repeat(3001-p.length)+' "quote" tail"}';
    assert.throws(()=>JSON.parse(raw),/Expected ',' or '}' after property value in JSON at position 3003/);
  });
  check("valid syntax can silently contain duplicate keys",()=>{
    assert.equal(JSON.parse('{"taskId":"first","taskId":"second"}').taskId,"second");
  });
  check("truncated JSON is not a complete response",()=>assert.throws(()=>JSON.parse('{"taskId":"mock-1"')));
  check("wrong task envelope rejected",()=>assert.throws(()=>decode('{"taskId":null}'),/invalid task envelope/));
  const scene={script:"A\n\nB",scenes:[{narration:"A",visualPrompt:"one"},{narration:"B",visualPrompt:"two"}]};
  check("valid storyboard accepted",()=>assert.deepEqual(validateScenes(JSON.stringify(scene),2),scene));
  check("syntactically valid wrong scene count rejected",()=>assert.throws(()=>validateScenes(JSON.stringify(scene),3),/schema mismatch/));
  check("syntactically valid inconsistent narration rejected",()=>assert.throws(()=>validateScenes(JSON.stringify({...scene,script:"A"}),2),/semantic mismatch/));
  check("naive retry duplicates remote effects after lost response",()=>{
    remote=[];assert.throws(()=>decode(provider(true)));decode(provider());assert.equal(remote.length,2);
  });
  check("durable marker freezes unknown outcome across fresh reads",()=>{
    fresh();remote=[];assert.throws(()=>submit("original prompt",true));assert.equal(load().state,"unknown");
    assert.throws(()=>submit("original prompt"),/ambiguous/);assert.equal(remote.length,1);
  });
  check("changed payload cannot clear existing submission",()=>{
    assert.throws(()=>submit("different prompt"),/payload mismatch/);assert.equal(remote.length,1);
  });
  check("reconciliation rejects missing remote identity",()=>assert.throws(()=>reconcile("missing"),/no verified remote match/));
  check("reconcile known original identity without another submission",()=>{
    reconcile("mock-1");assert.equal(submit("original prompt"),"mock-1");assert.equal(remote.length,1);
  });
  console.log(JSON.stringify({node:process.version,checks:results,passed:results.length,scope:"synthetic single-process local file journal and in-memory mock service; not production, no network, no actual cost, not a crash-consistency or concurrency proof",observations:{naiveRemoteEffects:2,guardedRemoteEffects:1}},null,2));
} finally {rmSync(dir,{recursive:true,force:true});}
