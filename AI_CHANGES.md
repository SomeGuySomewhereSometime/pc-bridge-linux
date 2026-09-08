# Change log

## 2026-09-08 — Independent distribution 0.5.0 (base history)

- Source: Bridge 0.4.1, revision `92c4151f308dd0b768475a45b4de3e2b0660359c`.
- Independent directory/repository without personal configuration, credentials,
  tunnels, or virtual environments from the source installation.
- Linux/PowerShell installers with preserved configuration and a separate Blender environment.
- X11/Windows adapters, bounded Windows search with path protection, and diagnostics.
- Windows rejects shell/Git/patch operations without isolation and does not pretend
  forceful process termination is a graceful editor close.
- Initial Portuguese guides covered installation, editor setup, and ChatGPT connections.
- Forty tests passed on Ubuntu 26.04/Python 3.14.4 with host Bubblewrap and systemd
  checks enabled, including real MCP stdio, path denial, sandboxed Git, and process lifecycle.
- Lifecycle tests were changed to supply temporary configuration explicitly.
- Bridge dependency checks passed; Blender dependencies were installed separately.
- Base CI included Ubuntu and Windows. Real screenshots, editor sessions, and a new
  ChatGPT connection still required manual acceptance.
- The vendored addon preserved upstream bytes, licensing, and provenance.
- Windows CI exposed short-path/canonical-path comparisons; roots are normalized
  before validation. Windows CI subsequently passed on Python 3.12 and 3.14
  (historical run 34217861245).
- The Blender wrapper imported and advertised 30 tools without an editor session.
- A Linux process-test race was fixed by waiting for the final executable identity
  before signaling; process authorization policy remained unchanged.

## 2026-09-08 — Independent Linux variant

Request: preserve PCBridgePortable and create a Linux-only installer in a new folder
with user instructions. Copied source without Git, venvs, or personal configuration.

Changed install.sh/setup_bridge.py to reject unsupported systems/root/WSL, check
Bubblewrap and prerequisites, validate paths before installation, create private
configuration, preserve existing settings, and run pip check and doctor. Added a
local MCP client example. run_bridge.py rejects other operating systems; CI targets
Ubuntu only. Removed install.ps1 from this copy. Added installation, diagnostics,
update/removal instructions and package.sh for a source archive with SHA-256.

Validation: fresh installation with --with-blender in a path containing spaces;
reinstallation preserved configuration. All 49 tests passed on the host, including
Bubblewrap/systemd integration. SHA-256 comparison confirmed 31 unchanged source files.
Two new tests were corrected to handle an already-configured installation folder.
See VALIDATION.md for desktop, editor, remote account, and distribution limitations.

## 2026-09-08 — Public GitHub repository

Request: create a public repository under SomeGuySomewhereSometime with a clear
name and explanation of its purpose. Published as pc-bridge-linux with an expanded
README, use cases, access boundaries, prerequisites, and clone instructions.
Preserved existing licenses and attribution without adding a new Bridge license.
Reviewed distribution contents to exclude credentials, personal settings, virtual
environments, and original Git history. Only the Linux variant was published.

## 2026-09-08 — English presentation and instructions

User requested English for the repository. Translated the README, installation,
client/editor guides, validation notes, change log, installer help/errors, and GitHub
description. Kept CLI options, dependency versions, permissions, and behavior unchanged.
Regenerated the distribution archive and verified the installer/tests before publishing.
