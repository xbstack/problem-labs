"""Offline runtime fixture; run only through isolated_runner.py.
FunctionModel is scripted, not an LLM. No provider requests.
"""
import asyncio,json,os,platform,resource,statistics,time,socket
from importlib.metadata import version
from pathlib import Path
from pydantic_ai import Agent,ModelResponse,TextPart,ToolCallPart,models
from pydantic_ai.models.function import FunctionModel,DeltaToolCall
from pydantic_ai_harness import CodeMode
models.ALLOW_MODEL_REQUESTS=False

async def trial(mode,n,delay):
    calls=[]; steps=[]
    async def model(messages,info):
        await asyncio.sleep(delay)
        calls.append(1)
        if mode=="native" and len(calls)<=n:
            return ModelResponse(parts=[ToolCallPart("advance",{"value":len(calls)-1})])
        if mode=="code" and len(calls)==1:
            code=f"x=0\nfor i in range({n}):\n    x=await advance(value=x)\nx"
            return ModelResponse(parts=[ToolCallPart("run_code",{"code":code})])
        return ModelResponse(parts=[TextPart("finished")])
    async def stream(messages,info):
        response=await model(messages,info)
        for part in response.parts:
            if isinstance(part,ToolCallPart):
                yield {0:DeltaToolCall(name=part.tool_name,json_args=json.dumps(part.args),tool_call_id="fixture-"+str(len(calls)))}
            else:
                yield part.content
    agent=Agent(FunctionModel(model,stream_function=stream),capabilities=[CodeMode()] if mode=="code" else [])
    @agent.tool_plain
    def advance(value:int)->int:
        """Increment a value in a deterministic dependent chain."""
        steps.append(value)
        return value+1
    t=time.perf_counter()
    result=await agent.run("Execute the predetermined increment chain.")
    elapsed=(time.perf_counter()-t)*1000
    assert steps==list(range(n)),(mode,steps,[(p.part_kind,str(getattr(p,'content',''))[:800]) for m in result.all_messages() for p in m.parts])
    assert len(calls)==(n+1 if mode=="native" else 2),(mode,len(calls))
    assert result.output=="finished"
    return {"ms":elapsed,"scripted_requests":len(calls),"tool_calls":len(steps)}

async def main():
    # The OS sandbox denies network; check using a local socket only.
    denied=False
    try:
        with socket.socket() as s:
            s.bind(("127.0.0.1",0))
    except OSError:
        denied=True
    assert denied,"network sandbox did not deny local binding"
    rows=[]
    for delay in (0,.025,.100):
        for n in (3,10):
            for mode in ("native","code"):
                await trial(mode,n,delay)
                samples=[await trial(mode,n,delay) for _ in range(5)]
                rows.append({"mode":mode,"steps":n,"injected_delay_ms":delay*1000,"repetitions":len(samples),"median_ms":round(statistics.median(x["ms"] for x in samples),2),"min_ms":round(min(x["ms"] for x in samples),2),"max_ms":round(max(x["ms"] for x in samples),2),"scripted_requests":samples[0]["scripted_requests"],"tool_calls":samples[0]["tool_calls"],"accepted":len(samples),"samples_ms":[round(x["ms"],2) for x in samples]})
    print(json.dumps({"scope":"real installed Pydantic AI/Harness, scripted FunctionModel, synthetic dependent tool chain and injected delays; not real model inference or Pax-vs-other-harness benchmark","network_bind_denied":denied,"python":platform.python_version(),"platform":platform.platform(),"versions":{x:version(x) for x in ("pydantic-ai-pax","pydantic-ai-harness","pydantic-ai-slim","pydantic-monty")},"rows":rows,"measured_runs":sum(x["repetitions"] for x in rows),"warmups":len(rows),"paid_model_calls":0,"peak_process_rss_raw":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},ensure_ascii=False))
if __name__=="__main__":
    asyncio.run(main())
