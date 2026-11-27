"""Read-only pinned wheel inspection and independent analysis of published SWE81 cells.
No installation, imports of downloaded code, extraction, model calls or shell commands.
Run: python3 experiments/pax-harness-evidence-20261127/audit.py
"""
import ast
import email
import hashlib
import io
import json
import platform
import statistics as stats
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

PACKAGES = [
    ("pydantic-ai-pax", "0.75.0", "5ddb05f11be38a0139258f31a5c002e34f0d84b3ee89e6d0b881c8ebb410e492"),
    ("pydantic-ai-harness", "0.75.0", "f8b0444375ee74d05660d3ce200face6b681c94a6356918a57daa8903c3ce6bd"),
    ("pydantic-ai-slim", "2.75.0", "eb51d50faf201ea63c8a0243523e21286d535c5cbc956628d6a3eac4afbf429f"),
]
# Published November 25 data: Pax, OpenCode, pi, deepagents-code, Codex, Claude Code.
# Scores are graded-task averages, NOT solved-task percentages. None = not reported.
NAMES = ["Pax", "OpenCode", "pi", "deepagents-code", "Codex", "Claude Code"]
ROWS = [
 ("GPT-6 Luna", [55.1,57.2,53.3,55.1,56.0,None],[.77,.69,.57,1.08,1.04,None]),
 ("GPT-6.1 Terra",[54.1,54.7,57.2,51.4,54.2,None],[4.97,5.41,3.97,13.79,6.36,None]),
 ("Claude Haiku 5.5",[56.0,55.5,52.9,59.1,None,56.5],[1.46,1.50,1.20,1.34,None,1.37]),
 ("Claude Sonnet 5.5",[58.4,60.8,57.9,57.7,None,56.9],[7.90,7.43,6.54,7.90,None,6.86]),
 ("MiniMax M3.1 Flash",[54.7,50.8,52.3,50.7,54.7,38.6],[1.67,2.94,1.40,2.92,1.85,2.95]),
 ("Kimi K3.1 Pro",[63.7,64.3,59.1,61.5,61.8,62.9],[10.92,9.81,9.44,11.88,14.42,11.40]),
 ("GPT-6.2 Sol",[64.7,61.0,64.8,61.7,60.1,None],[9.21,9.17,7.69,12.98,21.05,None]),
 ("Claude Opus 5.5",[61.2,61.4,61.1,63.3,None,60.4],[24.61,27.33,20.96,23.51,None,25.10]),
]
checks=[]
def check(name, value, evidence):
    checks.append({"name":name,"status":"PASS" if value else "FAIL","evidence":evidence})
    assert value, name

def retrieve(package, version, expected):
    request = f"https://pypi.org/pypi/{package}/{version}/json"
    with urllib.request.urlopen(request, timeout=20) as response:
        info=json.load(response)
    wheel=next(x for x in info["urls"] if x["filename"].endswith("py3-none-any.whl"))
    assert wheel["url"].startswith("https://files.pythonhosted.org/") and wheel["size"] < 20_000_000
    with urllib.request.urlopen(wheel["url"],timeout=20) as response:
        blob=response.read(20_000_001)
    sha=hashlib.sha256(blob).hexdigest()
    assert sha==expected==wheel["digests"]["sha256"]
    z=zipfile.ZipFile(io.BytesIO(blob))
    m=email.message_from_bytes(z.read(next(n for n in z.namelist() if n.endswith(".dist-info/METADATA"))))
    assert m["Version"]==version
    return z,m,{"package":package,"version":version,"sha256":sha,"wheel":wheel["filename"],"python_files":sum(n.endswith(".py") for n in z.namelist()),"python_requirement":m["Requires-Python"],"dependencies":[s for s in m.get_all("Requires-Dist",[]) if "pydantic-ai" in s and "extra ==" not in s]}

def tree(z,path):
    return ast.parse(z.read(path))
def symbols(z,path):
    return [n.name for n in tree(z,path).body if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef))]
def identifiers(z,path):
    return sorted({n.id for n in ast.walk(tree(z,path)) if isinstance(n,ast.Name)})

def main():
    data=[retrieve(*p) for p in PACKAGES]
    pax,harness,core=[p[0] for p in data]
    receipts=[p[2] for p in data]
    check("01 pinned wheel digests and versions",len(receipts)==3,receipts)
    deps=[r["dependencies"] for r in receipts]
    check("02 package coupling",any("==0.75.0" in x for x in deps[0]) and any("==2.75.0" in x for x in deps[0]) and any("==2.75.0" in x for x in deps[1]),deps)
    ep=pax.read(next(n for n in pax.namelist() if n.endswith("entry_points.txt"))).decode()
    check("03 console aliases","pax = pydantic_ai_pax.__main__:main" in ep and "pydantic-ai-pax = pydantic_ai_pax.__main__:main" in ep,ep)
    cp="pydantic_ai_pax/builtin_plugins/coder.py"
    ps="pydantic_ai_pax/plugins/__init__.py"
    cs="pydantic_ai_harness/coder/_capability.py"
    s={cp:symbols(pax,cp),ps:symbols(pax,ps),cs:symbols(harness,cs)}
    check("04 plugin versus SDK composition","CoderPlugin" in s[cp] and "Plugin" in s[ps] and "Coder" in s[cs],s)
    pp="pydantic_ai_pax/runtime/permissions.py"
    s=symbols(pax,pp)
    check("05 permission handling symbols",all(x in s for x in ["ApprovalHandler","approval_handler","session_permissions"]),s)
    relevant=["code_mode/_capability.py","code_mode/_toolset.py","code_mode/_streaming.py","code_mode/_speculation.py"]
    s={p:symbols(harness,"pydantic_ai_harness/"+p) for p in relevant}
    check("06 code mode components",len(s)==4,s)
    relevant=["compaction/_summarizing_compaction.py","compaction/_clear_tool_results.py","compaction/_deduplicate_file_reads.py","compaction/_context_window.py"]
    s={p:symbols(harness,"pydantic_ai_harness/"+p) for p in relevant}
    check("07 context management components",len(s)==4,s)
    relevant=["step_persistence/_capability.py","step_persistence/_store.py","step_persistence/recovery.py"]
    s={p:symbols(harness,"pydantic_ai_harness/"+p) for p in relevant}
    s["core model fallback"]=symbols(core,"pydantic_ai/capabilities/model_fallback.py")
    check("08 persistence and fallback separation","ModelFallback" in s["core model fallback"] and len(s)==4,s)
    means={NAMES[i]:{"score":stats.mean(r[1][i] for r in ROWS),"usd":stats.mean(r[2][i] for r in ROWS)} for i in range(4)}
    check("09 full-model coverage and arithmetic",len(ROWS)==8 and all(len(x[1])==len(x[2])==6 for x in ROWS) and round(means["Pax"]["score"],1)==58.5 and round(means["pi"]["usd"],2)==6.47,means)
    winners=[]
    for model,sc,cost in ROWS:
        valid=[i for i in range(6) if sc[i] is not None and cost[i] is not None]
        # Both no-worse, one strictly better.
        frontier=[NAMES[i] for i in valid if not any(sc[j]>=sc[i] and cost[j]<=cost[i] and (sc[j]>sc[i] or cost[j]<cost[i]) for j in valid if j!=i)]
        winners.append({"model":model,"highest_score":[NAMES[i] for i in valid if sc[i]==max(sc[j] for j in valid)],"lowest_cost":[NAMES[i] for i in valid if cost[i]==min(cost[j] for j in valid)],"pareto":frontier})
    check("10 no universal winner; Pareto analysis",all("pi" in w["lowest_cost"] or w["model"]=="Claude Haiku 5.5" for w in winners) and any("Pax" not in w["pareto"] for w in winners),winners)
    sol=(21.05-9.21)/21.05*100; opus=(25.10-24.61)/25.10*100
    sensitivity={"sol_cost_reduction_percent":sol,"opus_cost_reduction_percent":opus,"sol_relaxed_gap":round(64.7-60.1,1),"sol_stock_gap":round(51-49.8,1),"opus_relaxed_gap":round(61.2-60.4,1),"opus_stock_gap":round(54.9-53.5,1)}
    check("11 score and cost sensitivity",round(sol,1)==56.2 and round(opus,1)==2.0 and sensitivity["sol_stock_gap"]==1.2,sensitivity)
    # Synthetic scenario, not benchmark or measured price.
    c={"A":{"direct":10,"rework":50,"accepted":6},"B":{"direct":20,"rework":10,"accepted":8}}
    cpv={k:(x["direct"]+x["rework"])/x["accepted"] for k,x in c.items()}
    check("12 synthetic accepted-task cost inversion",c["A"]["direct"]<c["B"]["direct"] and cpv["A"]>cpv["B"],{"inputs":c,"cost_per_validated_task":cpv})
    result={"cutoff":"2026-11-27","checked_at":datetime.now(timezone.utc).isoformat(),"python":platform.python_version(),"platform":platform.platform(),"scope":"read-only wheel AST and vendor-published aggregate arithmetic; one illustrative synthetic calculation; no Pax runtime or provider calls","source":"https://pydantic.dev/articles/pax-harness-beta","packages":receipts,"benchmark":{"harnesses":NAMES,"rows":ROWS,"mean_four_complete":means,"per_model":winners,"sensitivity":sensitivity},"checks":checks,"passed":len(checks),"model_calls":0}
    Path(__file__).with_name("result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"passed":len(checks),"means":means,"per_model":winners,"sensitivity":sensitivity,"artifacts":receipts},ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
