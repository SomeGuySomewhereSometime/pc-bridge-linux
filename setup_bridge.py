"""Per-user Linux installer; installs only in this independent directory."""
import argparse
import json
import os
import platform
import shlex
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent


def python_in(folder):
    return folder / "bin/python"


def write_new(path, text):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(text)


def build_config(workspace, blender=None, unity=None, unity_project=None):
    workspace = workspace.expanduser().resolve()
    if workspace == Path.home() or workspace == Path(workspace.anchor):
        raise ValueError("Choose a dedicated projects folder, not your home or filesystem root")
    config_path = ROOT / "bridge_config.json"
    if config_path.exists():
        raise FileExistsError("Configuration already exists; edit it manually instead of overwriting it")
    if workspace.is_relative_to(ROOT) or ROOT.is_relative_to(workspace):
        raise ValueError("Keep the workspace separate from the installation folder")
    if workspace.exists() and not workspace.is_dir():
        raise ValueError("The selected projects path is a file")
    private = ROOT / ".local"
    config = {"workspace": str(workspace), "filesystem": {
        "denied_paths": [str(private), str(workspace / ".secrets")],
        "read_only_paths": [str(ROOT)]}, "applications": {},
        "process_kill": {"allowed_executables": [], "allowed_signals": ["TERM"]},
        "integrations": {"blender": {"port": 9876}, "unity": {"port": None}}}
    for alias, executable in (("blender", blender), ("unity", unity)):
        if not executable:
            continue
        exe = Path(executable).expanduser().resolve(strict=True)
        if not exe.is_file() or not os.access(exe, os.X_OK):
            raise ValueError("The application must be an executable file")
        args = []
        if alias == "unity":
            if not unity_project:
                raise ValueError("--unity requires --unity-project")
            project = Path(unity_project).expanduser().resolve(strict=True)
            if not project.is_dir() or not project.is_relative_to(workspace):
                raise ValueError("Unity project must be a directory inside the workspace")
            args = ["-projectPath", str(project)]
        config["applications"][alias] = {"executable": str(exe), "fixed_args": args,
            "allow_args": False, "running_executables": [str(exe)], "running_required_args": args}
    return config


def configure(workspace, blender=None, unity=None, unity_project=None):
    config = build_config(workspace, blender, unity, unity_project)
    Path(config["workspace"]).mkdir(parents=True, exist_ok=True)
    (ROOT / ".local").mkdir(mode=0o700, exist_ok=True)
    config_path = ROOT / "bridge_config.json"
    # Exclusive creation, private from the first byte (independent of the umask).
    fd = os.open(config_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(json.dumps(config, indent=2) + "\n")
    return config


def require_linux():
    if platform.system() != "Linux":
        raise ValueError("This installer supports native Linux only")
    if sys.version_info < (3, 12):
        raise ValueError("Python 3.12 or newer is required")
    if os.geteuid() == 0:
        raise ValueError("Run as a regular user, without sudo")
    if "microsoft" in platform.release().lower():
        raise ValueError("WSL is not supported by this Linux desktop installer")


def preflight():
    require_linux()
    for binary in ("bwrap", "git", "grep", "bash", "ps", "env", "true"):
        path = Path("/usr/bin") / binary
        if not path.is_file() or not os.access(path, os.X_OK):
            raise ValueError(f"Missing {path}. See docs/INSTALL.md")
    import ensurepip  # Fail before installation if the distro's venv support is missing.
    result = subprocess.run(["/usr/bin/bwrap", "--die-with-parent", "--unshare-all",
                             "--ro-bind", "/", "/", "--", "/usr/bin/true"],
                            capture_output=True, text=True, timeout=15)
    if result.returncode:
        raise ValueError("Bubblewrap cannot create a sandbox. See docs/INSTALL.md; "
                         "the installer does not disable isolation.")
    result = subprocess.run(["/usr/bin/systemctl", "--user", "show-environment"],
                            capture_output=True, timeout=10) if Path("/usr/bin/systemctl").exists() else None
    if result is None or result.returncode:
        print("Warning: user systemd manager unavailable; open editors manually.")
    if os.environ.get("XDG_SESSION_TYPE") == "wayland":
        result = subprocess.run(["/usr/bin/python3", "-c", "import dbus; from gi.repository import GLib"],
                                capture_output=True, timeout=10)
        if result.returncode:
            print("Warning: python3-dbus/python3-gi missing for Wayland screenshots; see the guide.")
    elif not os.environ.get("DISPLAY"):
        print("Warning: no graphical session detected; screenshots require an active desktop.")


def export_client_config():
    servers = {"pcbridge-linux": {"command": str(python_in(ROOT / ".venv")),
                                 "args": [str(ROOT / "run_bridge.py"), "stdio"]}}
    if python_in(ROOT / ".venv-blender").is_file():
        servers["blender-linux"] = {"command": str(python_in(ROOT / ".venv-blender")),
                                    "args": [str(ROOT / "ops/blender_entry.py")]}
    path = ROOT / ".local/mcp-client.json"
    if not path.exists():
        write_new(path, json.dumps({"mcpServers": servers}, indent=2) + "\n")
    else:
        print(".local/mcp-client.json preserved; if you added Blender, see docs/EDITORS.md.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.home() / "PCBridgeLinuxProjects")
    parser.add_argument("--blender", help="Absolute Blender executable path (optional)")
    parser.add_argument("--unity", help="Absolute Unity Editor executable path (optional)")
    parser.add_argument("--unity-project")
    parser.add_argument("--with-blender", action="store_true", help="Install the separate Blender MCP environment")
    parser.add_argument("--configure-only", action="store_true", help="Create configuration only; do not install dependencies")
    parser.add_argument("--check", action="store_true", help="Check prerequisites without installing")
    args = parser.parse_args()
    try:
        require_linux()
        if args.check:
            preflight()
            print("Basic Linux prerequisites verified. Warnings indicate missing optional capabilities.")
            return
        config_path = ROOT / "bridge_config.json"
        if config_path.exists():
            config = json.loads(config_path.read_text(encoding="utf-8"))
            workspace = Path(config["workspace"])
            if not workspace.is_absolute() or not workspace.is_dir():
                raise ValueError("Existing configuration does not point to a valid projects directory")
            print("Existing configuration preserved; workspace/application arguments were not applied.")
        else:
            build_config(args.workspace, args.blender, args.unity, args.unity_project)
        if not args.configure_only:
            preflight()
            environments = [(ROOT / ".venv", ROOT / "requirements.txt")]
            if args.with_blender:
                environments.append((ROOT / ".venv-blender", ROOT / "ops/blender-requirements.lock"))
            for folder, requirements in environments:
                if not folder.exists():
                    venv.EnvBuilder(with_pip=True).create(folder)
                subprocess.run([str(python_in(folder)), "-m", "pip", "install", "-r", str(requirements)], check=True)
                subprocess.run([str(python_in(folder)), "-m", "pip", "check"], check=True)
        if not config_path.exists():
            configure(args.workspace, args.blender, args.unity, args.unity_project)
        (ROOT / ".local").mkdir(mode=0o700, exist_ok=True)
        if args.configure_only:
            print("Configuration created/preserved. Dependencies were not installed.")
            return
        subprocess.run([str(python_in(ROOT / ".venv")), "-B", str(ROOT / "run_bridge.py"), "doctor"], check=True)
        export_client_config()
        print("Linux installation complete. MCP configuration: .local/mcp-client.json")
        print("Instructions: docs/INSTALL.md and docs/EDITORS.md")
        print(shlex.join([str(python_in(ROOT / ".venv")), str(ROOT / "run_bridge.py"), "doctor"]))
    except (ValueError, KeyError, ImportError, OSError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"Error: {exc}\nSee docs/INSTALL.md; retry installation after fixing the problem.\n")


if __name__ == "__main__":
    main()
