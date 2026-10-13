import os
import subprocess
from pathlib import Path


def test_ingestion_import_does_not_initialize_the_gateway_in_a_fresh_process(tmp_path):
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        ["uv", "run", "--no-project", "python", "-c", "import sys; import src.ingestion; assert 'src.gateway.app' not in sys.modules; print('fresh ingestion import passed')"],
        cwd=root,
        env={**os.environ, "OPENAI_API_KEY": "test-only-no-network", "CHROMA_PATH": str(tmp_path / "chroma")},
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
