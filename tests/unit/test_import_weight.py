"""The import-weight guard: `import calfkit` must not load heavy SDKs.

The public surface is pure vocabulary; transport/provider SDKs load only when
an adapter is explicitly used (the sole-importer contracts in pyproject.toml).
Runs in a subprocess so this test sees a clean module state.
"""

import subprocess
import sys

HEAVY_SDKS = ("aiokafka", "faststream", "litellm", "mcp")


def test_import_calfkit_loads_no_heavy_sdks() -> None:
    probe = (
        "import sys\n"
        "import calfkit\n"
        f"loaded = [m for m in {HEAVY_SDKS!r} if m in sys.modules]\n"
        "assert not loaded, f'import calfkit loaded: {loaded}'\n"
    )
    subprocess.run([sys.executable, "-c", probe], check=True)
