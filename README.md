# PC Bridge Linux

**Connect an MCP-compatible AI client to your Linux computer to work with local
files, commands, and projects.** Includes a per-user installer and guides for
connecting ChatGPT, Unity, and Blender.

**Unity and Blender integrations are included; the editors themselves are not installed
automatically.** Blender support includes the addon and an optional MCP server environment
installed with `--with-blender`; you must install Blender and enable the addon manually.
Unity support includes MCP setup instructions and a package configuration reference;
you must install Unity and enable its MCP plugin in your project.
See the [Unity and Blender setup guide](docs/EDITORS.md).

By **SurveysGuy** · X: [@someguy_112358](https://x.com/someguy_112358)

MCP (Model Context Protocol) lets an AI client discover and call the Bridge's
tools. This project does not include an AI model. You need an MCP client and,
for remote access from ChatGPT, your own account and tunnel connection.

## What it does

- Provides **20 MCP tools** for files, search, shell commands, Git, system
  diagnostics, screenshots, and authorized application management.
- Runs shell, Git, and patch operations through **Bubblewrap**, constrained by
  the configured workspace and filesystem policy, with networking disabled inside
  the command sandbox.
- Supports desktop screenshots through Wayland portals or X11, subject to desktop permissions.
- Optionally installs a separate Python environment for **Blender MCP**, with its addon included.
- Documents **Unity MCP** setup inside your project and how to connect all three
  servers. The Bridge handles files and commands; the editors own their live state.

## Why use it?

Use it when you want an assistant to work on Linux projects through explicit tools,
without repeatedly copying files and terminal output into a conversation. Examples
include investigating a project error, editing files in an authorized folder,
checking Git status, or combining code work with Unity and Blender tools.

The installer uses an independent directory and dedicated Python environments.
It preserves existing configuration when run again, making it easier to try the
integration alongside an existing setup and remove it later.

Your workspace is the folder you authorize the assistant to use. Its tools can
modify and delete files there: choose the projects you want to expose and configure
protected paths. The sandbox is a development boundary, not containment against
hostile processes running under the same local account. Editor MCPs have their own
permissions, including code execution inside the editor.

## Compatibility

**Tested on Ubuntu 26.04 LTS with Python 3.14.4 and systemd 259.** Other Linux
distributions may work if they meet the requirements, but have not been validated.
Requires Python 3.12+, venv, Git, and working Bubblewrap. Application launching
requires a compatible user systemd manager; screenshots require a graphical session.
The installer rejects Windows, macOS, and WSL.

## Quick start

On Ubuntu/Debian with Python 3.12 or newer, install the system dependencies and
clone into a permanent directory owned by your user:

```sh
sudo apt install python3 python3-venv git bubblewrap
git clone https://github.com/SomeGuySomewhereSometime/pc-bridge-linux.git PCBridgeLinux
cd PCBridgeLinux
sh install.sh --check
sh install.sh --workspace "$HOME/PCBridgeLinuxProjects"
.venv/bin/python run_bridge.py doctor
```

Use `sudo` only for the system package manager, not for the installer.
Add `--with-blender` to install the separate Blender MCP Python environment.
Installation downloads the pinned Python dependencies inherited from the base project.

**[Full installation guide](docs/INSTALL.md)** · [Unity and Blender](docs/EDITORS.md) ·
[MCP clients and ChatGPT](docs/CHATGPT.md) · [Validation and limitations](VALIDATION.md)

The installer generates `.local/mcp-client.json` with absolute paths for clients
that accept `mcpServers`. You do not need to activate the virtual environment.
Account/tunnel setup and editor addon activation are manual steps covered in the guides.

## Scope

- Native Linux, with Wayland or X11 for desktop features.
- A working Bubblewrap sandbox is mandatory for a full installation.
- Wayland screenshots depend on the desktop portal and user consent; X11 uses MSS.
- Editors can be opened manually when compatible user systemd is unavailable.
- Existing configuration is preserved. Projects are kept outside the installation directory.
- The installer does not create services or change other installations, accounts, or projects.

## Provenance and licensing

Derived from the local PCBridgePortable source snapshot dated 2026-09-08. Changes
focus on the Linux installer, entry point, documentation, and CI. Shared internal
modules retain adapters and tests from the base; they do not imply Windows support
in this distribution.

The Blender addon retains its [original MIT license](ops/vendor/blender-mcp/LICENSE).
The base project does not specify a redistribution license for the Bridge code;
this repository does not add one.

## Build a distribution archive

Run `sh package.sh` to create `PCBridgeLinux.tar.gz` and its SHA-256 file in the
parent directory. The archive includes source, documentation, and the addon,
while excluding virtual environments, personal configuration, `.local`, and Git history.
Share that archive rather than a configured installation directory.
