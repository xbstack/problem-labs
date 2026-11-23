# GHSA-764m-3ppc-5m73 — read-only local detection validation

## Scope

Only tests a **benign synthetic replica of package metadata and file names** for agent-framework 1.26.1 and 1.26.2. This repository does not contain either malicious wheel. It does not run, install, load, import or download malicious code. The scanner never executes .pth content, and the tests run under `python -S` to prevent interpreter site initialization.

Source evidence: https://github.com/advisories/GHSA-764m-3ppc-5m73 and https://www.elastic.co/security-labs/threat-command/we-caught-the-agent-framework-pypi-compromise-six-minutes-after-it-published

## User benefit

Read-only inspection of copied wheel names/metadata, requirements/lock pin, or a detached site-packages directory; flag both startup hooks (`agent_framework_meta.pth` for 1.26.1 and `af_runtime_diag.pth` for 1.26.2). Output contains **no secret contents**.

## Run

```sh
python3 -S -m unittest discover -s experiments/agent-framework-pypi-20261123 -p 'test_*.py' -v
python3 -S experiments/agent-framework-pypi-20261123/scan.py /path/to/copied-requirements.txt
```

Do not run this on a machine you suspect is still compromised using its own potentially tainted interpreter. Use a trusted offline interpreter / disk image. Flagged evidence means potential exposure, not proven exfiltration; negative results cannot rule out removed artifacts, temporary CI agents, remote caches or compromised credentials.

If affected, isolate affected systems, investigate with a security team, rebuild from trusted sources and rotate secrets reachable by that workload, including ephemeral CI/OIDC cloud credentials where applicable. Do not treat `pip uninstall` as incident containment.
