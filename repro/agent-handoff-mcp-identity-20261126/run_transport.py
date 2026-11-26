"""Install pinned packages into an ephemeral venv and remove it automatically."""
import json, os, pathlib, subprocess, sys, tempfile, venv
env={k:v for k,v in os.environ.items() if not k.startswith(("OPENAI_","ANTHROPIC_","GOOGLE_API_","AZURE_OPENAI_","HF_TOKEN"))}
env["NO_PROXY"]="127.0.0.1,localhost"
env["no_proxy"]="127.0.0.1,localhost"
env["PYTHONUNBUFFERED"]="1"
with tempfile.TemporaryDirectory(prefix="sdk-transport-fixture-") as td:
    venv.EnvBuilder(with_pip=True).create(td)
    python=str(pathlib.Path(td)/"bin/python")
    install=subprocess.run([python,"-m","pip","install","--disable-pip-version-check","--no-input","--no-cache-dir","openai-agents==0.26.0","mcp==2.3.0","uvicorn==0.52.1"],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=100)
    print(json.dumps({"install_exit":install.returncode,"install_tail":install.stdout.splitlines()[-5:]}))
    if install.returncode:sys.exit(install.returncode)
    result=subprocess.run([python,str(pathlib.Path(__file__).with_name("transport_fixture.py"))],env=env,timeout=35)
    sys.exit(result.returncode)
