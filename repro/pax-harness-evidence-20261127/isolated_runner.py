"""Create disposable installation, restrict home reads and writes, then deny network.
No project files, account credentials, or production data are given to the child.
"""
import os,sys,subprocess,tempfile,shutil,json,time
from pathlib import Path
import platform
def main():
    here=Path(__file__).resolve().parent
    uv=Path.home()/".local/bin/uv"
    with tempfile.TemporaryDirectory(prefix="pax-lab-",dir="/private/tmp") as t:
        root=Path(t).resolve()
        for n in ("home","tmp","work","cache"): (root/n).mkdir()
        shutil.copy2(uv,root/"uv")
        shutil.copy2(here/"runtime_probe.py",root/"work/runtime_probe.py")
        env={"HOME":str(root/"home"),"TMPDIR":str(root/"tmp"),"PATH":str(root/"venv/bin")+":/opt/homebrew/bin:/usr/bin:/bin","UV_CACHE_DIR":str(root/"cache"),"UV_NO_PROGRESS":"1","UV_PYTHON_DOWNLOADS":"never","LANG":"en_US.UTF-8","PYTHONDONTWRITEBYTECODE":"1"}
        base='(version 1) (allow default) (deny file-read* (subpath "/Users")) (deny file-write* (require-all (require-not (subpath "'+str(root)+'")) (require-not (literal "/dev/null"))))'
        def run(args,offline,timeout):
            profile=base+(' (deny network*)' if offline else '')
            r=subprocess.run(["/usr/bin/sandbox-exec","-p",profile,*map(str,args)],cwd=root/"work",env=env,capture_output=True,text=True,timeout=timeout)
            if r.returncode:
                print("FAILED",args[0],r.returncode,r.stderr[-4500:],r.stdout[-1000:],flush=True)
                raise SystemExit(1)
            return r
        run([root/"uv","--no-config","venv","--python",os.path.realpath(sys.executable),root/"venv"],False,20)
        run([root/"uv","--no-config","pip","install","--python",root/"venv/bin/python","--only-binary",":all:","--index-url","https://pypi.org/simple","pydantic-ai-pax==0.75.0","pydantic-ai-harness[coder,codemode]==0.75.0","pydantic-ai-slim==2.75.0"],False,90)
        print("PINNED INSTALL OK",flush=True)
        help_result=run([root/"venv/bin/pydantic-ai-pax","--help"],True,20)
        print("CLI HELP OK",flush=True)
        r=run([root/"venv/bin/python",root/"work/runtime_probe.py"],True,90)
        result=json.loads(r.stdout.strip().splitlines()[-1])
        result["cli_help_exit"]=help_result.returncode
        result["cli_help_mentions_pax"]="pax" in help_result.stdout.lower()
        result["machine"]="Apple M1 Pro / 10 CPU cores / 16 GiB unified memory"
        result["environment_cleanup"]="TemporaryDirectory removed after execution"
        (here/"runtime-result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
        print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=="__main__":
    main()
