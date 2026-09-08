"""Platform adapters. Unsupported capabilities fail explicitly."""
from pathlib import Path
import os
import platform
import shutil
import socket
import subprocess
import time

from fastapi import HTTPException


def search_files(root, check_path, query):
    """Bounded literal search; prune protected directories before reading files."""
    output = []
    size = 0
    visited = 0
    deadline = time.monotonic() + 30
    def files():
        if root.is_file():
            yield root
            return
        for folder, directories, names in os.walk(root, followlinks=False):
            kept = []
            for name in directories:
                candidate = Path(folder) / name
                if name in {".git", "node_modules", ".venv"} or candidate.is_symlink():
                    continue
                try:
                    check_path(str(candidate))
                    kept.append(name)
                except HTTPException:
                    pass
            directories[:] = kept
            for name in names:
                yield Path(folder) / name
    for file in files():
        visited += 1
        if visited > 10000 or time.monotonic() > deadline:
            return {"matches": "\n".join(output), "truncated": True}
        if file.is_symlink():
            continue
        try:
            allowed = check_path(str(file))
            if not allowed.is_file() or allowed.stat().st_size > 2_000_000:
                continue
            for number, line in enumerate(allowed.read_text(encoding="utf-8").splitlines(), 1):
                if query in line:
                    entry = f"{file}:{number}:{line}"
                    size += len(entry)
                    if size > 100000:
                        return {"matches": "\n".join(output), "truncated": True}
                    output.append(entry)
        except (HTTPException, OSError, UnicodeError):
            continue
    return {"matches": "\n".join(output), "truncated": False}


def capture_desktop(destination: Path, interactive: bool, include_cursor: bool) -> str:
    if interactive:
        raise HTTPException(501, "Interactive selection requires the Wayland portal; use interactive=false here")
    try:
        import mss
        import mss.tools
        with mss.mss(with_cursor=include_cursor) as capture:
            shot = capture.grab(capture.monitors[0])
            mss.tools.to_png(shot.rgb, shot.size, output=str(destination))
    except Exception as exc:
        raise HTTPException(503, f"Desktop capture unavailable: {exc}") from exc
    return "mss-windows" if platform.system() == "Windows" else "mss-x11"


def windows_process_list(req) -> dict:
    import psutil
    result = []
    limit = max(1, min(req.limit, 1000))
    attributes = ["pid", "ppid", "username", "status", "create_time", "name"]
    if req.include_args:
        attributes.append("cmdline")
    for proc in psutil.process_iter(attributes, ad_value=None):
        info = proc.info
        item = dict(pid=info["pid"], ppid=info["ppid"], user=info["username"],
                    state=info["status"], elapsed=max(0, time.time() - (info["create_time"] or time.time())),
                    command=info["name"])
        if req.include_args:
            item["args"] = subprocess.list2cmdline(info["cmdline"] or [])
        if req.query.casefold() not in " ".join(map(str, item.values())).casefold():
            continue
        result.append(item)
        if len(result) >= limit:
            break
    return dict(processes=result, count=len(result), limit=limit, include_args=req.include_args)


def existing_application(policy: dict) -> int | None:
    import psutil
    allowed = {os.path.normcase(str(Path(x).resolve())) for x in policy.get("running_executables", [])}
    required = policy.get("running_required_args", [])
    username = psutil.Process().username()
    for proc in psutil.process_iter(["exe", "cmdline", "username"], ad_value=None):
        info = proc.info
        if info["username"] != username or not info["exe"]:
            continue
        if os.path.normcase(str(Path(info["exe"]).resolve())) not in allowed:
            continue
        args = info["cmdline"] or []
        if required and not any(args[i:i+len(required)] == required for i in range(len(args))):
            continue
        return proc.pid
    return None


class WindowsApplication:
    """Popen retains the owned process handle; never signal an arbitrary reused PID."""
    unit = "windows-detached"

    def __init__(self, process):
        self.process = process
        self.pid = process.pid

    @property
    def returncode(self):
        return self.process.returncode

    def poll(self):
        return self.process.poll()

    def terminate(self):
        # Popen.terminate on Windows is forceful, not a graceful editor close.
        raise HTTPException(501, "Close the editor normally to save work; force=true explicitly terminates the owned process")

    def kill(self):
        self.process.kill()

    def wait(self, timeout):
        return self.process.wait(timeout=timeout)


def launch_windows(argv, cwd, environment):
    flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    proc = subprocess.Popen(argv, cwd=cwd, env=environment, stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            creationflags=flags, close_fds=True)
    return WindowsApplication(proc)


def diagnostics(workspace: Path, config: dict) -> dict:
    """No editor mutation, no arbitrary diagnostic commands or remote URLs."""
    integrations = {}
    for name in ("unity", "blender"):
        port = config.get("integrations", {}).get(name, {}).get("port")
        item = {"configured": port is not None, "tcp_reachable": False,
                "editor_verified": False}
        if isinstance(port, int) and not isinstance(port, bool) and 1 <= port <= 65535:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=1):
                    item["tcp_reachable"] = True
            except OSError:
                pass
        integrations[name] = item
    linux = platform.system() == "Linux"
    return {"platform": platform.system(), "session": os.environ.get("XDG_SESSION_TYPE", "unknown"),
            "workspace_exists": workspace.is_dir(),
            "bubblewrap_installed": linux and Path("/usr/bin/bwrap").is_file(),
            "shell_platform_supported": linux,
            "systemd_run_installed": bool(shutil.which("systemd-run")),
            "integrations": integrations,
            "note": "TCP reachability does not verify MCP, the active project, scene, or enabled tools."}
