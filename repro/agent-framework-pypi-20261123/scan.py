#!/usr/bin/env python3
"""Read-only, offline exposure indicators for GHSA-764m-3ppc-5m73.

SAFETY:
* Does not import agent-framework, load site-packages, execute .pth, extract
  wheel contents, read credential files, or open network connections.
* Run from a trusted interpreter, ideally 'python -S ...', on copies of
  lockfiles/wheels/directory listings from an isolated machine.
* A match is an exposure *indicator*, not proof of exfiltration. Absence of
  a match cannot prove a previously installed environment was clean.

Examples:
 python3 -S scan.py /path/to/requirements.txt /path/to/agent_framework-1.26.1-py3-none-any.whl
 python3 -S scan.py /path/to/offline/site-packages/
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

BAD_VERSIONS = {"1.26.1", "1.26.2"}
HOOKS = {
    "agent_framework_meta.pth": "1.26.1",
    "af_runtime_diag.pth": "1.26.2",
}
HELPERS = {
    "agent_framework_meta/_telemetry.py": "1.26.1",
    "af_runtime_diag.py": "1.26.2",
}
# Only inspect exact local text files, not arbitrary .env or credential material.
MANIFESTS = {"requirements.txt", "requirements.in", "uv.lock", "poetry.lock", "pipfile.lock"}
PIN_RE = re.compile(r"(?im)\bagent[-_]framework\s*(?:\[.*?\])?\s*==\s*(1\.26\.[12])\b")
LOCK_RE = re.compile(r'(?ims)\bname\s*=\s*["\']agent-framework["\']\s*\n\s*version\s*=\s*["\'](1\.26\.[12])["\']')
WHEEL_RE = re.compile(r'(?i)\bagent[_-]framework[-_](1\.26\.[12])(?:[-_]|\b)')
METADATA_NAME = re.compile(r"(?im)^Name:\s*agent-framework\s*$")
METADATA_VERSION = re.compile(r"(?im)^Version:\s*(1\.26\.[12])\s*$")


def inspect_listing(display: str, names: list[str], metadata: list[str] | None = None) -> list[dict]:
    hits: list[dict] = []
    normalized = [n.replace("\\", "/").lstrip("/") for n in names]
    for name in normalized:
        basename = name.rsplit("/", 1)[-1]
        if basename in HOOKS and ("/" not in name or "/site-packages/" in "/" + name):
            hits.append({"indicator": "startup_hook", "name": basename,
                         "associated_version": HOOKS[basename]})
        for helper, version in HELPERS.items():
            if name == helper or name.endswith("/" + helper):
                hits.append({"indicator": "helper_module", "name": helper,
                             "associated_version": version})
    if metadata:
        for m in metadata:
            if METADATA_NAME.search(m):
                version = METADATA_VERSION.search(m)
                if version:
                    hits.append({"indicator": "installed_metadata_version",
                                 "name": "agent-framework", "version": version.group(1)})
    return hits


def inspect(path: Path) -> dict:
    info: dict = {"path": str(path), "kind": None, "indicators": [], "error": None}
    if path.is_dir():
        info["kind"] = "offline_directory"
        names: list[str] = []
        metadata: list[str] = []
        for child in path.rglob("*"):
            if not child.is_file():
                continue
            relative = child.relative_to(path).as_posix()
            if child.name in HOOKS or child.name in {x.rsplit("/", 1)[-1] for x in HELPERS}:
                names.append(relative)
            elif child.name == "METADATA" and "agent_framework" in relative.lower() and child.stat().st_size < 32768:
                metadata.append(child.read_text(encoding="utf8", errors="replace"))
        info["indicators"] = inspect_listing(str(path), names, metadata)
    elif path.is_file() and path.suffix == ".whl":
        info["kind"] = "wheel_archive_names_only"
        match = WHEEL_RE.search(path.name)
        if match:
            info["indicators"].append({"indicator": "wheel_filename_version",
                                       "version": match.group(1)})
        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
            metadata = [zf.read(n).decode("utf8", errors="replace")
                        for n in names if n.endswith(".dist-info/METADATA")
                        and zf.getinfo(n).file_size < 32768]
            info["indicators"].extend(inspect_listing(str(path), names, metadata))
    elif path.is_file() and (path.name.lower() in MANIFESTS or path.suffix in {".lock", ".txt"}):
        info["kind"] = "dependency_manifest"
        if path.stat().st_size > 2_000_000:
            raise ValueError("manifest too large (limit 2 MiB)")
        data = path.read_text(encoding="utf8", errors="replace")
        matches = sorted(set(PIN_RE.findall(data) + LOCK_RE.findall(data)))
        info["indicators"] = [
            {"indicator": "locked_bad_version", "name": "agent-framework", "version": v}
            for v in matches
        ]
    else:
        info["kind"] = "not_supported"
        info["error"] = "Expected a copied site-packages directory, wheel, or lock/requirements file."
    info["flagged"] = bool(info["indicators"])
    return info


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("offline_paths", nargs="+", type=Path)
    args = parser.parse_args(argv)
    entries = []
    for path in args.offline_paths:
        try:
            entries.append(inspect(path))
        except (OSError, zipfile.BadZipFile, ValueError) as exc:
            entries.append({"path": str(path), "error": str(exc), "flagged": None})
    result = {"advisory": "GHSA-764m-3ppc-5m73", "mode": "offline_read_only",
              "samples_examined": len(entries), "flagged": sum(x.get("flagged") is True for x in entries),
              "inconclusive": sum(x.get("flagged") is None for x in entries), "results": entries,
              "caution": ("Indicators only: absence is not proof of safety. If a malicious version ran, "
                          "isolate affected hosts, rebuild from trusted media, and rotate exposed secrets.")}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result["flagged"] else (1 if result["inconclusive"] else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
