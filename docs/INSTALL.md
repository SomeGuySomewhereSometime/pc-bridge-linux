# Linux installation guide

## 1. Prepare your computer

Use native Linux and a terminal in your normal user session. Check:

```sh
python3 --version
echo "$XDG_SESSION_TYPE"
```

Python must be 3.12 or newer. Graphical sessions may use `wayland` or `x11`.
Files and commands work without a desktop; screenshots require an active graphical
session. Windows, macOS, and WSL are not supported by this package.

On Ubuntu/Debian, install the system dependencies:

```sh
sudo apt install python3 python3-venv git bubblewrap
```

Your distribution must provide Python 3.12+. Install the venv package matching
your Python version. On other distributions, use equivalent packages; this codebase
expects Linux utilities under `/usr/bin`.

For Wayland screenshots:

```sh
sudo apt install python3-dbus python3-gi xdg-desktop-portal
```

You also need your desktop's portal backend, such as `xdg-desktop-portal-gnome`
for GNOME or `xdg-desktop-portal-kde` for KDE. Install the appropriate backend.
The screenshot helper uses `/usr/bin/python3` and its system modules.
For X11, you need `libx11-6` and valid session `DISPLAY`/`XAUTHORITY` settings.

## 2. Get the source and install

Clone into a permanent location owned by your user:

```sh
git clone https://github.com/SomeGuySomewhereSometime/pc-bridge-linux.git PCBridgeLinux
cd PCBridgeLinux
```

Alternatively, extract a distribution archive into a permanent folder, such as
`~/Applications/PCBridgeLinux`, and open a terminal in the folder containing `install.sh`.

```sh
sh install.sh --check
sh install.sh --workspace "$HOME/PCBridgeLinuxProjects"
```

Do not run the installer with sudo. The projects folder may already contain your
projects, but must be separate from the installation. Do not use your entire home
directory or `/`. Without `--workspace`, the default is `~/PCBridgeLinuxProjects`.
Python dependency downloads require access to PyPI or your configured pip index.

To include Blender MCP:

```sh
sh install.sh --workspace "$HOME/PCBridgeLinuxProjects" --with-blender
```

The installer creates:

| Path inside the installation | Purpose |
|---|---|
| `.venv/` | Bridge Python environment and dependencies |
| `.venv-blender/` | Separate environment, only with `--with-blender` |
| `bridge_config.json` | Authorized workspace, filesystem policy, and applications |
| `.local/` | Private installation data |
| `.local/mcp-client.json` | MCP example using this installation's absolute paths |

The projects folder is created if needed. Installation checks Python dependencies
and runs diagnostics. It does not create services, tunnel profiles, or accounts.
An interrupted installation may leave a partial venv: fix the cause and run the
same command again.

## 3. Verify and connect

```sh
.venv/bin/python run_bridge.py doctor
.venv/bin/python -B check.py
```

Diagnostics report prerequisites and local ports; they do not establish editor
readiness. Normal tests use disposable data and skip some host integration checks.
To also test sandboxing and the systemd launcher on your computer:

```sh
BRIDGE_SANDBOX_TESTS=1 BRIDGE_SYSTEMD_TESTS=1 .venv/bin/python -B check.py
```

These checks create temporary test processes and service units, not editor sessions.
Follow [MCP clients and ChatGPT](CHATGPT.md) to connect a client, and
[Unity and Blender](EDITORS.md) for editor setup. The Bridge exposes 20 MCP tools.

## 4. Configuration and daily use

Your MCP client starts `run_bridge.py stdio` using the Python executable in `.venv`.
Starting it by itself in a terminal may simply wait: stdio requires an MCP client.
After editing the JSON configuration, restart only this installation's connection.

You can register applications during the first installation:

```sh
sh install.sh --workspace "$HOME/PCBridgeLinuxProjects" \
  --blender /usr/bin/blender
```

Use an executable that exists on your computer. For Unity, add
`--unity /path/to/Editor/Unity --unity-project /path/to/project`.
The Unity project must be inside the workspace. Quote paths containing spaces.

After installation, edit `applications` in `bridge_config.json` manually. Re-running
the installer preserves the JSON and ignores new workspace/application arguments.
For Snap or special launchers, open the editor manually or explicitly configure the
launcher, fixed arguments, and process identity. Do not enable arbitrary arguments
for shells or interpreters.

Files in the workspace can be modified. Keep secrets outside it, or add their paths
to `filesystem.denied_paths`. `workspace/.secrets` is blocked by default.
Do not include `.local` or your personal configuration when distributing the package.

## 5. Troubleshooting

| Problem | Action |
|---|---|
| Old Python, missing venv/ensurepip | Install Python 3.12+ and its matching venv package |
| pip/download failure | Check the network/index and retry; installation is incomplete until pip and doctor succeed |
| Bubblewrap cannot create a sandbox | Use native Linux and check user namespaces and distribution policy; do not disable isolation |
| `systemctl --user` unavailable | Use your normal user session or open editors manually |
| Unsupported systemd options | The launcher uses `--expand-environment=no` and `ExitType=cgroup`; open editors manually on older versions |
| Wayland screenshots fail | Check portal/backend, system dbus/gi modules, and desktop consent |
| X11 screenshots fail | Check the active session, libX11, and DISPLAY/XAUTHORITY |
| Editor port unreachable | Open the editor, enable its addon/plugin, and check the configured integration port |
| Client still uses old paths | After moving the installation, recreate its venvs and update client paths; prefer installing in the final location |

`--check` verifies prerequisites without installing or creating configuration.
`--configure-only` creates configuration and the projects folder only; it does not
verify dependencies, sandbox execution, or MCP readiness.

## 6. Reinstall, update, and remove

You can rerun the installer in the same folder. It preserves `bridge_config.json`
and the existing MCP example. If you add Blender later, add its client entry as
explained in [EDITORS.md](EDITORS.md). Edit the JSON to change the workspace.

For a new version, install in a new folder and test before switching the client
connection. Keep the previous installation until the replacement is verified.

To remove this installation, disable its MCP client connection and stop only the
tunnel/profile you created for it, if any. Remove its client entries, then delete
the installation folder using your file manager. Keep the separate projects folder.
Remove any addons or services you installed manually through their respective
applications if you no longer need them.
