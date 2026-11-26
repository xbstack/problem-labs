"""Run SDK source-level offline regression using exact tagged official PyPI wheels, no model/API calls."""
import ast, hashlib, json, urllib.request, zipfile, io, sys, copy, platform, datetime, pathlib
from typing import Any
VERSIONS=("0.25.0","0.26.0")
PINNED_SHA256={"0.25.0":"09a02b815842b498647749a8d9e4c101b0bd69d2a81a8f91e8ec3ac0f2c54150","0.26.0":"c3f9545035e46a5a17c88eec789e2301efe26eca230fccab0fc4a6961c0f02e1"}
result={"scope":"isolated original MCPUtil metadata merge method extracted from verified PyPI wheels; not full SDK transport/handoff/OAuth test","python":platform.python_version(),"checkedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"versions":{},"errors":[]}
for version in VERSIONS:
 try:
  req=urllib.request.Request(f"https://pypi.org/pypi/openai-agents/{version}/json",headers={"User-Agent":"XBSTACK reproducibility research"})
  with urllib.request.urlopen(req,timeout=15) as f: info=json.load(f)
  wheels=[x for x in info["urls"] if x["filename"].endswith(".whl")]
  assert len(wheels)==1
  wheel=wheels[0]
  with urllib.request.urlopen(wheel["url"],timeout=25) as f: data=f.read(10000000)
  sha=hashlib.sha256(data).hexdigest()
  assert sha==wheel["digests"]["sha256"]==PINNED_SHA256[version]
  with zipfile.ZipFile(io.BytesIO(data)) as z: src=z.read("agents/mcp/util.py").decode()
  tree=ast.parse(src)
  cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="MCPUtil")
  fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="_merge_mcp_meta")
  fn.decorator_list=[]
  ns={"Any":Any,"copy":copy}
  marker=next((n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="_DiscoveredToolMeta"),None)
  body=([marker] if marker else [])+[fn]
  module=ast.fix_missing_locations(ast.Module(body=body,type_ignores=[]))
  exec(compile(module,"<verified-wheel-method>","exec"),ns)
  merge=ns["_merge_mcp_meta"]
  def discovered(d):return ns["_DiscoveredToolMeta"](d) if marker else d
  # Invented labels only; not authentication credentials.
  defaults={"tenant":"default","locale":"en","nested":{"x":1}}
  resolver={"tenant":"request","trace":"request-1"}
  merged=merge(resolver,discovered(defaults))
  explicit=merge(resolver,{"tenant":"explicit"})
  no_meta=merge(None,None)
  out=merge(resolver,discovered(defaults));out["nested"]["x"]=9
  tests={"discovery_collision":merged.get("tenant")==("request" if version=="0.26.0" else "default"),"explicit_precedence":explicit["tenant"]=="explicit","non_conflicting_preserved":merged["locale"]=="en" and merged["trace"]=="request-1","empty_metadata":no_meta is None,"nested_copy_isolation":defaults["nested"]["x"]==1}
  result["versions"][version]={"wheel":wheel["filename"],"sha256":sha,"source_file":"agents/mcp/util.py","source_sha256":hashlib.sha256(src.encode()).hexdigest(),"function":fn.name,"discovery_marker_in_wheel":bool(marker),"collision_result":merged["tenant"],"explicit_result":explicit["tenant"],"tests":tests}
 except Exception as e:result["errors"].append({"version":version,"type":type(e).__name__,"message":str(e)[:180]})
result["passed"]=sum(sum(v["tests"].values()) for v in result["versions"].values())
result["total"]=10
pathlib.Path(__file__).with_name("sdk-source-result.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result))
sys.exit(0 if result["passed"]==10 and not result["errors"] else 1)
