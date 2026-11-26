"""Real SDK + MCP loopback handoff fixture. No model API, no real tokens, no external services."""
from contextlib import AsyncExitStack
import asyncio, datetime, hashlib, importlib.metadata as md, json, os, socket, threading, time
from pathlib import Path
import uvicorn
from mcp.server.mcpserver import MCPServer
from agents import Agent, Runner, RunConfig
from agents.mcp import MCPServerStreamableHttp
from agents.testing import ModelStep, ScriptedModel, assistant_message, function_call

events=[]
service=MCPServer(name="local-fixture")
@service.tool()
async def read_fixture(item: str)->str:
    """Read a synthetic record."""
    return "synthetic:"+item

class Observe:
    def __init__(self, app): self.app=app
    async def __call__(self, scope, receive, send):
        if scope["type"]!="http":
            return await self.app(scope,receive,send)
        messages=[]
        while True:
            event=await receive()
            messages.append(event)
            if event["type"]!="http.request" or not event.get("more_body",False):break
        try:
            payload=json.loads(b"".join(m.get("body",b"") for m in messages))
        except (ValueError,TypeError): payload={}
        if isinstance(payload,dict) and payload.get("method")=="tools/call":
            params=payload.get("params") or {}
            credential=dict(scope["headers"]).get(b"authorization",b"")
            events.append({"credential_sha256":hashlib.sha256(credential).hexdigest(),"agent_label":(params.get("_meta") or {}).get("fixture_actor"),"tool":params.get("name")})
        async def replay():
            if messages:return messages.pop(0)
            return await receive()
        return await self.app(scope,replay,send)

def step(call_id):
    return ModelStep.respond(lambda call:[function_call(next(t.name for t in call.tools if t.name.endswith("read_fixture")),{"item":"sample"},call_id=call_id)])

def resolver(meta):
    return {"fixture_actor":meta.run_context.agent.name}

async def scenario(url,separate):
    before=len(events)
    a=MCPServerStreamableHttp(name="local",params={"url":url,"headers":{"Authorization":"Bearer SYNTHETIC-FIXTURE-TRIAGE"}},tool_meta_resolver=resolver)
    b=MCPServerStreamableHttp(name="local",params={"url":url,"headers":{"Authorization":"Bearer SYNTHETIC-FIXTURE-SPECIALIST"}},tool_meta_resolver=resolver) if separate else a
    specialist=Agent(name="specialist",mcp_servers=[b],model=ScriptedModel([step("call-b"),[assistant_message("complete")]]))
    triage=Agent(name="triage",mcp_servers=[a],handoffs=[specialist],model=ScriptedModel([step("call-a"),ModelStep.respond(lambda c:[function_call(c.handoffs[0].tool_name,{},call_id="handoff")])]))
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(a)
        if separate: await stack.enter_async_context(b)
        await Runner.run(triage,"read synthetic record",run_config=RunConfig(tracing_disabled=True))
    data=events[before:]
    return {"separate_client_objects":separate,"calls":data,"assertions":{"two_calls":len(data)==2,"actor_labels": [x["agent_label"] for x in data]==["triage","specialist"],"credential_relation":len(data)==2 and (data[0]["credential_sha256"]!=data[1]["credential_sha256"])==separate}}

async def main():
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM);sock.bind(("127.0.0.1",0));port=sock.getsockname()[1]
    app=Observe(service.streamable_http_app(stateless_http=True,json_response=True))
    server=uvicorn.Server(uvicorn.Config(app,log_level="warning",access_log=False))
    thread=threading.Thread(target=server.run,kwargs={"sockets":[sock]},daemon=True);thread.start()
    try:
        for _ in range(100):
            if server.started:break
            await asyncio.sleep(.05)
        assert server.started
        results=[await scenario(f"http://127.0.0.1:{port}/mcp",False),await scenario(f"http://127.0.0.1:{port}/mcp",True)]
    finally:
        server.should_exit=True;thread.join(timeout=5);sock.close()
    payload={"versions":{p:md.version(p) for p in ["openai-agents","mcp","uvicorn"]},"checkedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"scope":"loopback real SDK and MCP HTTP; ScriptedModel; dummy credentials; no OAuth verification or production service","cases":results,"passed":sum(sum(x["assertions"].values()) for x in results),"total":6}
    print(json.dumps(payload))
    Path(__file__).with_name("transport-result.json").write_text(json.dumps(payload,indent=2)+"\n")
    assert payload["passed"]==payload["total"]

if __name__=="__main__":
    asyncio.run(main())
