"""Provider verification — reads the pact file and verifies the actual provider."""

from pathlib import Path
import pytest
from pact import Verifier


PACT_DIR = Path(__file__).parent.parent / "pacts"
PROVIDER_URL = "http://localhost:9000"


class TestProviderVerification:
    """验证 provider 能满足所有 consumer 的 pact 契约。"""

    def test_verify_pacts(self):
        pact_files = list(PACT_DIR.glob("*.json"))
        if not pact_files:
            pytest.skip("pacts 目录下没有契约文件。先运行 tests/test_pact_consumer.py 生成。")

        verifier = Verifier(name="qtcloud_write_provider")

        for pact_file in pact_files:
            verifier.add_source(str(pact_file))

        verifier.add_transport(url=PROVIDER_URL)
        result = verifier.verify()
        assert result == 0, "契约验证失败"
