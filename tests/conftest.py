import subprocess
import time
import signal
import pytest
import httpx
from pathlib import Path

PROVIDER_PORT = 8002
STUDIO_PORT = 8080
PROVIDER_URL = f"http://localhost:{PROVIDER_PORT}"
STUDIO_URL = f"http://localhost:{STUDIO_PORT}"
ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def provider():
    proc = subprocess.Popen(
        ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(PROVIDER_PORT)],
        cwd=ROOT / "src/provider",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        try:
            httpx.get(f"{PROVIDER_URL}/docs", timeout=2)
            break
        except httpx.ConnectError:
            time.sleep(0.5)
    else:
        proc.kill()
        raise RuntimeError("Provider failed to start")
    yield proc
    proc.send_signal(signal.SIGTERM)
    proc.wait(timeout=10)


@pytest.fixture(scope="session")
def flutter_build():
    result = subprocess.run(
        ["flutter", "build", "web", "--dart-define", f"API_URL={PROVIDER_URL}"],
        cwd=ROOT / "src/studio",
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"flutter build web failed:\n{result.stderr}"
    return ROOT / "src/studio/build/web"


@pytest.fixture(scope="session")
def studio_server(flutter_build):
    proc = subprocess.Popen(
        ["python3", "-m", "http.server", str(STUDIO_PORT), "--directory", str(flutter_build)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    yield proc
    proc.kill()
    proc.wait(timeout=5)
