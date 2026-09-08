"""Stable entry point for MCP clients, independent of their working directory."""
import argparse
import json
import os
from pathlib import Path
import runpy
import platform

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["stdio", "doctor"], nargs="?", default="stdio")
    args = parser.parse_args()
    if platform.system() != "Linux":
        parser.error("This distribution supports Linux only")
    config_path = Path(os.environ.get("BRIDGE_CONFIG", ROOT / "bridge_config.json")).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    workspace = Path(config["workspace"]).expanduser()
    if not workspace.is_absolute() or not workspace.is_dir():
        parser.error("Configured workspace must be an existing absolute directory")
    os.environ["BRIDGE_CONFIG"] = str(config_path)
    os.environ["BRIDGE_WORKSPACE"] = str(workspace.resolve())
    if args.mode == "doctor":
        from security import validate_filesystem_policy
        from portable import diagnostics
        validate_filesystem_policy(config)
        print(json.dumps(diagnostics(workspace, config), indent=2))
    else:
        runpy.run_path(str(ROOT / "mcp_server.py"), run_name="__main__")


if __name__ == "__main__":
    main()
