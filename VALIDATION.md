# Linux validation — 2026-09-08

## Verified locally

- Full installation in a temporary folder containing spaces, with fresh virtual
  environments, pinned dependency downloads, and `--with-blender`: successful.
- `pip check` passed in both the Bridge and Blender environments.
- `run_bridge.py doctor` completed successfully through the installer.
- Re-running the installer preserved configuration byte for byte. A new workspace
  argument was ignored and that directory was not created.
- All 49 tests passed on the Linux host using Python 3.14, with no skipped tests,
  with `BRIDGE_SANDBOX_TESTS=1 BRIDGE_SYSTEMD_TESTS=1`.
- Coverage includes a real MCP stdio session, 20 advertised tools, rejection of
  reads outside the workspace, Bubblewrap isolation, Git, and application survival
  after stopping its launcher.
- Nine installer tests cover rejection of unsupported systems/root/WSL, validation
  before changes, permissions, configuration preservation, and paths containing spaces.
- SHA-256 comparison of the 31 original source files confirmed no changes to the base.

The initial run inside the task sandbox could not create Bubblewrap namespaces and
encountered an MCP initialization timeout. Full checks ran on the host, preserving
the Bridge's own isolation. Two new tests were corrected because they incorrectly
assumed the installation directory could not already contain configuration.

## Not yet validated locally

- Installation on other distributions, Python 3.12, or other architectures. The CI
  workflow targets Ubuntu with Python 3.12 and 3.14; see GitHub Actions for current results.
- Real Wayland/X11 screenshots from this copy; automated tests exercise the adapters.
- A new ChatGPT account/tunnel, Unity Play Mode, or a Blender addon connected to this copy.
- Reboot/login and automatic startup. This package does not install services.

Installing Blender's Python environment does not verify an editor connection.
An open port does not establish project/scene identity or working editor tools.
