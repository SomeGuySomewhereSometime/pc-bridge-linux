"""Instalador Linux por utilizador; instala apenas nesta pasta independente."""
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
        raise ValueError("A pasta de projetos indicada é um ficheiro")
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
            raise ValueError("A aplicação deve ser um ficheiro executável")
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
        raise ValueError("Este instalador suporta apenas Linux nativo")
    if sys.version_info < (3, 12):
        raise ValueError("É necessário Python 3.12 ou superior")
    if os.geteuid() == 0:
        raise ValueError("Execute como utilizador normal, sem sudo")
    if "microsoft" in platform.release().lower():
        raise ValueError("WSL não é suportado por este instalador de desktop Linux")


def preflight():
    require_linux()
    for binary in ("bwrap", "git", "grep", "bash", "ps", "env", "true"):
        path = Path("/usr/bin") / binary
        if not path.is_file() or not os.access(path, os.X_OK):
            raise ValueError(f"Falta {path}. Consulte docs/INSTALL.md")
    import ensurepip  # Fail before installation if the distro's venv support is missing.
    result = subprocess.run(["/usr/bin/bwrap", "--die-with-parent", "--unshare-all",
                             "--ro-bind", "/", "/", "--", "/usr/bin/true"],
                            capture_output=True, text=True, timeout=15)
    if result.returncode:
        raise ValueError("Bubblewrap não consegue criar a sandbox. Consulte docs/INSTALL.md; "
                         "a instalação não desativa o isolamento.")
    result = subprocess.run(["/usr/bin/systemctl", "--user", "show-environment"],
                            capture_output=True, timeout=10) if Path("/usr/bin/systemctl").exists() else None
    if result is None or result.returncode:
        print("Aviso: gestor systemd de utilizador indisponível; abra os editores manualmente.")
    if os.environ.get("XDG_SESSION_TYPE") == "wayland":
        result = subprocess.run(["/usr/bin/python3", "-c", "import dbus; from gi.repository import GLib"],
                                capture_output=True, timeout=10)
        if result.returncode:
            print("Aviso: faltam python3-dbus/python3-gi para capturas Wayland; consulte o guia.")
    elif not os.environ.get("DISPLAY"):
        print("Aviso: sessão gráfica não detetada; capturas precisam de um desktop ativo.")


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
        print(".local/mcp-client.json preservado; se adicionou Blender, consulte docs/EDITORS.md.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.home() / "PCBridgeLinuxProjects")
    parser.add_argument("--blender", help="Caminho absoluto do executável Blender (opcional)")
    parser.add_argument("--unity", help="Caminho absoluto do Unity Editor (opcional)")
    parser.add_argument("--unity-project")
    parser.add_argument("--with-blender", action="store_true", help="Instalar ambiente separado do Blender MCP")
    parser.add_argument("--configure-only", action="store_true", help="Criar só configuração; não instalar dependências")
    parser.add_argument("--check", action="store_true", help="Verificar requisitos sem instalar")
    args = parser.parse_args()
    try:
        require_linux()
        if args.check:
            preflight()
            print("Requisitos básicos Linux verificados. Os avisos indicam capacidades opcionais em falta.")
            return
        config_path = ROOT / "bridge_config.json"
        if config_path.exists():
            config = json.loads(config_path.read_text(encoding="utf-8"))
            workspace = Path(config["workspace"])
            if not workspace.is_absolute() or not workspace.is_dir():
                raise ValueError("A configuração existente não aponta para uma pasta de projetos válida")
            print("Configuração existente preservada; argumentos de workspace/aplicações não aplicados.")
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
            print("Configuração criada/preservada. Dependências não instaladas.")
            return
        subprocess.run([str(python_in(ROOT / ".venv")), "-B", str(ROOT / "run_bridge.py"), "doctor"], check=True)
        export_client_config()
        print("Instalação Linux concluída. Configuração MCP: .local/mcp-client.json")
        print("Instruções: docs/INSTALL.md e docs/EDITORS.md")
        print(shlex.join([str(python_in(ROOT / ".venv")), str(ROOT / "run_bridge.py"), "doctor"]))
    except (ValueError, KeyError, ImportError, OSError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"Erro: {exc}\nConsulte docs/INSTALL.md; pode repetir a instalação após corrigir o problema.\n")


if __name__ == "__main__":
    main()
