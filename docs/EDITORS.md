# Unity and Blender setup

These reference versions come from the source installation inspected on 2026-09-08.
They do not imply that every combination has been tested.

| Component | Reference version |
|---|---|
| Unity Editor | 6000.6.0f1 |
| AI Game Developer / Unity MCP | 0.90.0 |
| GameDev MCP Server managed by the plugin | 9.2.5 |
| Blender | 5.2.1 LTS |
| Included Blender addon | 1.6, protocol 5 |
| Blender MCP Python server | 1.9.1, MCP SDK 1.30.0 |
| Bridge MCP SDK | 2.2.0, separate environment |

## Unity

1. Install Unity Hub and a Linux Editor compatible with your project. Check
   `ProjectSettings/ProjectVersion.txt`: opening a project in another version can
   migrate it. Test the integration on a project copy.
2. Install **AI Game Developer** using the author's
   [installation guide](https://github.com/IvanMurzak/Unity-MCP/wiki/Installation-Guide).
   It covers unitypackage, OpenUPM, and Package Manager methods. The source guide
   states Unity 2022.3 as a minimum; this copy's reference is Unity 6000.6.0f1.
   Prefer a project path without spaces, as advised by the plugin guide.
3. To reproduce the reference, use the OpenUPM scopes in
   `ops/config/unity/packages-mcp.json` and select `com.ivanmurzak.unity.mcp` 0.90.0.
   This JSON is a merge reference: do not replace an existing project's
   `Packages/manifest.json` or lock file. Enable optional extensions only when needed
   and inspect the dependencies Unity resolves.
4. Open `Window > AI Game Developer`, wait for compilation/server download, and
   confirm the connection. Enable `keepConnected`/`keepServerRunning` if desired.
   The [official configuration guide](https://github.com/IvanMurzak/Unity-MCP/wiki/Configuration)
   describes `UserSettings/AI-Game-Developer-Config.json`. Record the project's actual
   address and port. Keep the managed server version aligned with its plugin.
5. Check that tools such as `scene-list-opened`, `editor-application-get-state`,
   `console-get-logs`, `screenshot-game-view`, and `screenshot-scene-view` are enabled.
   Installed tools or generated skills do not prove a tool is enabled.
6. Configure the client using the plugin window. For tunneling, use the local MCP
   endpoint reported by the effective configuration (`streamableHttp`, with `/mcp`
   when indicated). Keep unauthenticated endpoints on loopback.
7. Verify the project identity, open scenes, and Console through MCP. For gameplay
   work, also test Play Mode and inspect Game View. Compilation alone is insufficient.
   Use a disposable scene and deliberately choose when to save.

Unity licensing, activation, and build modules are managed by the user through Hub.
The Bridge installer does not activate licenses, migrate projects, or enable editor tools.

## Blender

1. Install Blender for Linux. Run this package's installer with `--with-blender` to
   create `.venv-blender`. Keep its MCP 1.x dependencies separate from the Bridge's MCP 2.x.
2. In `Edit > Preferences > Add-ons`, choose **Install from Disk** (or **Install**,
   depending on the version), select `ops/vendor/blender-mcp/blender_mcp.py`, enable
   **MCP for Blender**, and save preferences. Use the included matching addon.
3. In the 3D viewport, press `N`, open **MCP for Blender**, and start its server.
   Confirm loopback `127.0.0.1`, port `9876`, and no errors. See the
   [author's guide](https://github.com/ahujasid/blender-mcp) for the addon panel.
   If you enable auto-start, save the setting and test reopening Blender.
4. External resources such as Sketchfab, Poly Haven, and 3D generation are optional
   and may need separate accounts or keys. They are unnecessary for reading scenes
   or running Blender code. The Python wrapper disables server telemetry; also
   review the addon's consent settings.
5. Configure a stdio client using the absolute path to `.venv-blender/bin/python`
   and the absolute script argument `ops/blender_entry.py`. Keep Blender open with
   the addon running. Do not start the server inside Blender's Python console.
   If you installed Blender support later, add this entry to your MCP client manually;
   the installer preserves an existing `.local/mcp-client.json`.
6. Request `get_context`, `get_scene_objects`, and a viewport screenshot. Confirm
   scene, file, and object identity before editing. Test changes in disposable files
   and verify them visually in Blender.

The addon can execute Python with your user account's permissions. Addon/script
consent is manual; do not disable Blender's protections globally to bypass errors.
