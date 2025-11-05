import subprocess
import sys
from pathlib import Path

def test_run_synthetic_demo_script():
    """
    Try to run bgcr-budyko/examples/run_synthetic_demo.py (if present) as a smoke test.
    If the script is not present, fall back to run_demo.sh if available.
    This test is intentionally lenient; it asserts the script exits with code 0.
    """
    repo_root = Path(__file__).resolve().parents[2]
    script1 = repo_root / "bgcr-budyko" / "examples" / "run_synthetic_demo.py"
    script2 = repo_root / "bgcr-budyko" / "run_demo.sh"

    if script1.exists():
        cmd = [sys.executable, str(script1)]
    elif script2.exists():
        cmd = [str(script2)]
    else:
        # Skip the test if no demo script is present
        import pytest
        pytest.skip("No demo script found to run.")

    res = subprocess.run(cmd, cwd=str(repo_root / "bgcr-budyko"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    assert res.returncode == 0, f"Demo script failed: stdout={res.stdout.decode()[:200]} stderr={res.stderr.decode()[:200]}"