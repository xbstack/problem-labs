"""Read-only availability check; never download weights, call a paid provider, or start a runtime."""
import json,urllib.request,urllib.error,re,datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
BASE="https://huggingface.co"
urls={
 "exact_space_search":BASE+"/api/spaces?search=bonsai-2.5&limit=30",
 "mlx_provider_mapping":BASE+"/api/models/prism-ml/Ternary-Bonsai-2.5-27B-mlx-2bit?expand=inferenceProviderMapping",
 "official_older_hosted_demo":BASE+"/spaces/prism-ml/Ternary-Bonsai-27B-Demo/raw/main/app.py",
 "local_ollama":"http://127.0.0.1:11434/api/tags",
 "local_lm_studio":"http://127.0.0.1:1234/v1/models"
}
def fetch(item):
    k,url=item
    out={"url":url}
    for attempt in range(2):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"XBSTACK metadata-only check"}),timeout=6) as r:
                data=r.read(200001)
                out={"url":url,"http":r.status,"bytesRead":len(data)}
                if len(data)>200000:out["error"]="cap";return k,out
                if k=="official_older_hosted_demo":
                    out["modelIds"]=sorted(set(re.findall(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]*[Bb]onsai[A-Za-z0-9_.-]*',data.decode("utf8","replace"))))
                else:
                    j=json.loads(data)
                    if k=="exact_space_search":out["spaces"]=[{"id":x.get("id"),"sdk":x.get("sdk")} for x in j]
                    elif k=="mlx_provider_mapping":out["providers"]=j.get("inferenceProviderMapping")
                    else:
                        # Never expose unrelated local model names.
                        models=j.get("models",j.get("data",[]))
                        out["exactVersionPresent"]=any(re.search(r'bonsai[-_ .]*2[._-]5.*27b',str(x.get("name",x.get("id",""))),re.I) for x in models)
                return k,out
        except urllib.error.HTTPError as e:return k,{"url":url,"http":e.code}
        except Exception as e:out={"url":url,"errorType":type(e).__name__}
    return k,out
with ThreadPoolExecutor(max_workers=5) as pool: results=dict(pool.map(fetch,urls.items()))
report={"checkedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"readOnly":True,"inferenceCalls":0,"checks":results}
Path(__file__).with_name("inference-routes.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
