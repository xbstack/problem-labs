"""Metadata-only verification, no weights download, no paid inference, stdlib only."""
import json, urllib.request, urllib.error, re, datetime, hashlib, math, sys, platform, shutil, subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
BASE="https://huggingface.co"
REPO="prism-ml/Ternary-Bonsai-2.5-27B-GGUF"
SPACE="webml-community/ternary-bonsai-2-webgpu-kernels"
CAP=2200000
def get(url,limit=CAP):
    req=urllib.request.Request(url,headers={"User-Agent":"XBSTACK metadata-only research","Accept-Encoding":"identity"})
    try:
        with urllib.request.urlopen(req,timeout=15) as r:
            n=r.headers.get("Content-Length")
            if n and int(n)>limit:return None,{"http":r.status,"error":"size_cap","declared":int(n),"bytesRead":0}
            data=r.read(limit+1)
            if len(data)>limit:return None,{"http":r.status,"error":"size_cap","bytesRead":len(data)}
            return data,{"http":r.status,"bytesRead":len(data),"sha256":hashlib.sha256(data).hexdigest()}
    except urllib.error.HTTPError as e:return None,{"http":e.code,"bytesRead":0}
    except Exception as e:return None,{"errorType":type(e).__name__,"bytesRead":0}
def retry_get(url,limit=CAP):
    import time
    for attempt in range(3):
        data,receipt=get(url,limit)
        if data is not None or receipt.get("http") in (400,401,403,404):return data,receipt
        if attempt<2:time.sleep(1)
    return data,receipt
def as_json(url):
    raw,receipt=retry_get(url)
    try:return json.loads(raw) if raw else {},receipt
    except ValueError:return {},{**receipt,"error":"invalid_json"}
jobs={
 "model":BASE+"/api/models/"+REPO+"?blobs=true",
 "tree":BASE+"/api/models/"+REPO+"/tree/main?recursive=false&expand=false",
 "providers":BASE+"/api/models/"+REPO+"?expand=inferenceProviderMapping",
 "mlx_search":BASE+"/api/models?author=prism-ml&search=Ternary-Bonsai-2.5-27B&limit=20",
 "spaces_search":BASE+"/api/spaces?search=ternary-bonsai&limit=40",
 "demo":BASE+"/spaces/"+SPACE+"/raw/main/index.html",
 "base_config":BASE+"/Qwen/Qwen3.8-27B/raw/main/config.json"
}
def fetch_job(item):
    k,url=item
    if k=="demo":
        data,receipt=get(url)
        text=data.decode("utf8","replace") if data else ""
        ids=sorted(set(re.findall(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]*[Bb]onsai[A-Za-z0-9_.-]*',text)))[:30]
        return k,{"modelIds":ids,"mentionsBonsai25":bool(re.search(r'Bonsai[-_ ]2[.\-_]5',text,re.I)),"webgpu":bool(re.search(r'webgpu',text,re.I)),"browserLocalLoading":bool(re.search(r'from_pretrained|fromPretrained|navigator\.gpu|onnxruntime|ort\.InferenceSession',text,re.I)),"sourceUrl":url},receipt
    data,receipt=as_json(url);return k,data,receipt
with ThreadPoolExecutor(max_workers=5) as pool: raw={k:(v,r) for k,v,r in pool.map(fetch_job,jobs.items())}
model=raw["model"][0];tree=raw["tree"][0]
files=[{"name":x["path"],"bytes":x["size"],"sha256":(x.get("lfs") or {}).get("oid")} for x in tree if isinstance(x,dict) and x.get("path","").endswith(".gguf") and isinstance(x.get("size"),int)] if isinstance(tree,list) else []
if not files:
    files=[{"name":x["rfilename"],"bytes":x["size"],"sha256":(x.get("lfs") or {}).get("sha256")} for x in model.get("siblings",[]) if x.get("rfilename","").endswith(".gguf") and isinstance(x.get("size"),int)]
files.sort(key=lambda x:x["name"])
sizes={x["name"]:x["bytes"] for x in files}
def lookup(suffix):return next((v for k,v in sizes.items() if k.endswith(suffix)),None)
ptq=lookup("-PTQ1_0.gguf");pq=lookup("-PQ2_0.gguf");q2=lookup("-Q2_0.gguf")
base=raw["base_config"][0]
cfg=base.get("text_config",base)
fields={k:cfg.get(k) for k in ("num_hidden_layers","num_attention_heads","num_key_value_heads","head_dim","hidden_size","max_position_embeddings","full_attention_interval","layer_types") if k in cfg}
mlx=raw["mlx_search"][0];mlx_ids=[x.get("id") for x in mlx if isinstance(x,dict) and "mlx" in x.get("id","").lower()] if isinstance(mlx,list) else []
spaces=raw["spaces_search"][0]
space_ids=[{"id":x.get("id"),"sdk":x.get("sdk")} for x in spaces if isinstance(x,dict)] if isinstance(spaces,list) else []
provider=raw["providers"][0].get("inferenceProviderMapping") if isinstance(raw["providers"][0],dict) else None
tests={}
def check(name,result):tests[name]=bool(result)
check("five_trits_fit_one_byte",3**5<=256<3**6)
# A teaching codec, NOT the actual PTQ1_0 decoder. Exhaustive roundtrip.
def pack(t):return sum((v+1)*3**i for i,v in enumerate(t))
def unpack(b):return tuple((b//3**i)%3-1 for i in range(5))
import itertools
all_trits=list(itertools.product((-1,0,1),repeat=5))
check("243_ternary_groups_roundtrip",all(unpack(pack(t))==t for t in all_trits))
check("243_unique_codes",len(set(map(pack,all_trits)))==243)
check("group_128_scale_overhead",math.isclose(16/128,.125))
check("dense_128_padded_bytes",math.ceil(128/5)==26)
check("dense_group_bits",math.isclose((26*8+16)/128,1.75))
check("two_bit_group_bits",math.isclose((128*2+16)/128,2.125))
check("one_gib_bytes",2**30==1073741824)
if ptq and pq and q2:
    check("three_real_packings_present",True)
    check("ptq_smaller_than_pq_and_q2",ptq<pq<q2)
    check("mtp_larger_than_base",all(lookup("-"+x+"-mtp.gguf")>lookup("-"+x+".gguf") for x in ("PTQ1_0","PQ2_0","Q2_0")))
    check("vision_separate",lookup("-mmproj-BF16.gguf")>lookup("-mmproj-Q8_0.gguf")>0)
# KV calculation ONLY conventional full-attention portion; no linear state/workspace included.
kv=[]
layers=fields.get("layer_types") or []
full=sum(t=="full_attention" for t in layers)
if not full and isinstance(fields.get("full_attention_interval"),int) and fields.get("num_hidden_layers"):full=fields["num_hidden_layers"]//fields["full_attention_interval"]
heads=fields.get("num_key_value_heads");dim=fields.get("head_dim")
if full and heads and dim:
    per=2*full*heads*dim*2
    for n in (4096,8192,32768,131072,262144):
        kv.append({"tokens":n,"bytes":n*per,"GiB":round(n*per/2**30,4)})
report={"checkedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"scope":"public artifact metadata and synthetic codec arithmetic only; no model inference, no performance/accuracy benchmark","repo":REPO,"revision":model.get("sha"),"files":files,"baseConfigFields":fields,"fullAttentionLayers":full,"fp16FullAttentionKVOnly":kv,"providerMapping":provider,"spaceCandidates":space_ids,"demo":raw["demo"][0],"mlxRepos":mlx_ids,"receipts":{k:{"url":jobs[k],**r} for k,(_,r) in raw.items()},"tests":tests,"passed":sum(tests.values()),"total":len(tests),"fullWeightsDownloadedBytes":0,"installedDependencies":0,"paidCalls":0,"inferenceCalls":0,"python":platform.python_version()}
Path(__file__).with_name("result.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(report,ensure_ascii=False))
required_metadata=bool(model.get('sha') and len(files)==8 and len(kv)==5 and raw['demo'][1].get('http')==200 and raw['providers'][1].get('http')==200)
sys.exit(0 if required_metadata and len(tests)==12 and all(tests.values()) else 1)
