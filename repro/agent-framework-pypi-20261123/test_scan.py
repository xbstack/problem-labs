"""Synthetic fixtures only; no downloaded packages, no executable startup hooks."""
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("scan.py")


class OfflineScannerTest(unittest.TestCase):
    def run_scan(self, *paths):
        p = subprocess.run([sys.executable, "-S", str(SCRIPT), *map(str, paths)],
                           capture_output=True, text=True, check=False)
        self.assertIn(p.returncode, (0, 1, 2))
        return p.returncode, json.loads(p.stdout)

    def test_requirements_pin_and_clean(self):
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "requirements.txt"
            bad.write_text("agent-framework==1.26.1\n", encoding="utf8")
            code, result = self.run_scan(bad)
            self.assertEqual(code, 2)
            self.assertEqual(result["flagged"], 1)
            bad.write_text("agent-framework==1.26.0\n", encoding="utf8")
            code, result = self.run_scan(bad)
            self.assertEqual(code, 0)
            self.assertEqual(result["flagged"], 0)

    def test_both_wheel_versions_by_names_only(self):
        for version, hook in (("1.26.1", "agent_framework_meta.pth"),
                              ("1.26.2", "af_runtime_diag.pth")):
            with tempfile.TemporaryDirectory() as d:
                wheel = Path(d) / f"agent_framework-{version}-py3-none-any.whl"
                with zipfile.ZipFile(wheel, "w") as z:
                    # .pth content is deliberately nonexecutable synthetic data.
                    z.writestr(hook, "# BENIGN TEST FIXTURE; DO NOT EXECUTE\n")
                    z.writestr(f"agent_framework-{version}.dist-info/METADATA",
                               f"Name: agent-framework\nVersion: {version}\n")
                code, result = self.run_scan(wheel)
                self.assertEqual(code, 2)
                found = result["results"][0]["indicators"]
                self.assertTrue(any(x["indicator"] == "startup_hook" for x in found))

    def test_copied_installed_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "af_runtime_diag.pth").write_text("# inert copy\n")
            (root / "agent_framework-1.26.2.dist-info").mkdir()
            (root / "agent_framework-1.26.2.dist-info" / "METADATA").write_text(
                "Name: agent-framework\nVersion: 1.26.2\n")
            code, result = self.run_scan(root)
            self.assertEqual(code, 2)
            self.assertGreaterEqual(len(result["results"][0]["indicators"]), 2)


if __name__ == "__main__":
    unittest.main()
