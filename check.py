"""Run tests with disposable configuration, without touching user settings."""
import json
import os
from pathlib import Path
import tempfile
import unittest

with tempfile.TemporaryDirectory(prefix="pcbridge-check-") as temporary:
    root = Path(temporary)
    config = root / "policy.json"
    config.write_text(json.dumps({"filesystem": {"denied_paths": [str(root / "secret")],
                                                "read_only_paths": [str(config)]}}))
    os.environ["BRIDGE_CONFIG"] = str(config)
    os.environ["BRIDGE_WORKSPACE"] = str(root)
    loader = unittest.TestLoader()
    suite = loader.discover(str(Path(__file__).parent), pattern="test_*.py") if os.name != "nt" else loader.loadTestsFromName("test_portable")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(not result.wasSuccessful())
