import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

from fastapi import HTTPException
import bridge
import portable
import security
import setup_bridge


class PortableTests(unittest.TestCase):
    def test_windows_shell_fails_before_spawning(self):
        with patch.object(security.sys, "platform", "win32"), patch.object(security.subprocess, "run") as run:
            with self.assertRaises(HTTPException) as error:
                security.run_sandbox(Path.cwd(), Path.cwd(), {}, ["cmd", "/c", "echo test"])
            self.assertEqual(error.exception.status_code, 501)
            run.assert_not_called()

    def test_configuration_is_new_private_and_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "install"
            root.mkdir()
            workspace = Path(temp) / "projects"
            with patch.object(setup_bridge, "ROOT", root):
                config = setup_bridge.configure(workspace)
                self.assertEqual(config["applications"], {})
                self.assertEqual(config["process_kill"]["allowed_executables"], [])
                security.validate_filesystem_policy(config)
                with self.assertRaises(FileExistsError):
                    setup_bridge.configure(workspace)
                self.assertEqual(json.loads((root / "bridge_config.json").read_text()), config)

    def test_windows_environment_omits_tokens(self):
        with patch.object(security.sys, "platform", "win32"), patch.dict(os.environ, {"AWS_SECRET_ACCESS_KEY": "synthetic", "SystemRoot": "C:\\Windows"}):
            env = security.minimal_environment(desktop=True)
            self.assertNotIn("AWS_SECRET_ACCESS_KEY", env)
            self.assertEqual(env["SystemRoot"], "C:\\Windows")

    def test_x11_capture_dispatches_without_portal(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def capture(destination, interactive, cursor):
                destination.write_bytes(b"test-png")
                return "mss-x11"
            with patch.object(bridge, "WORKSPACE", root), patch.object(bridge, "BRIDGE_CONFIG", {}), patch.object(bridge.platform, "system", return_value="Linux"), patch.dict(os.environ, {"XDG_SESSION_TYPE": "x11"}), patch.object(portable, "capture_desktop", side_effect=capture), patch.object(bridge, "_portal_capture") as portal:
                result = bridge.screen_capture(bridge.ScreenCaptureRequest(path="shot.png"))
                self.assertEqual(result["backend"], "mss-x11")
                portal.assert_not_called()

    def test_interactive_capture_is_not_silently_ignored(self):
        with self.assertRaises(HTTPException):
            portable.capture_desktop(Path("unused.png"), True, True)

    def test_windows_graceful_close_never_forces(self):
        process = Mock(pid=12)
        app = portable.WindowsApplication(process)
        with self.assertRaises(HTTPException):
            app.terminate()
        process.terminate.assert_not_called()
        process.kill.assert_not_called()
        app.kill()
        process.kill.assert_called_once()

    def test_file_roundtrip_and_escape_denial_on_native_os(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(bridge, "WORKSPACE", root), patch.object(bridge, "BRIDGE_CONFIG", {}):
                bridge.write_file(bridge.WriteRequest(path="hello.txt", content="Olá"))
                self.assertEqual(bridge.read_file(bridge.PathRequest(path="hello.txt"))["content"], "Olá")
                with self.assertRaises(HTTPException):
                    bridge.read_file(bridge.PathRequest(path="../outside.txt"))
                bridge.move(bridge.MoveRequest(source="hello.txt", destination="renamed.txt"))
                bridge.delete(bridge.DeleteRequest(path="renamed.txt"))
                self.assertFalse((root / "renamed.txt").exists())

    def test_diagnostics_does_not_claim_editor_validation(self):
        with patch.object(portable.socket, "create_connection", side_effect=OSError):
            result = portable.diagnostics(Path.cwd(), {"integrations": {"blender": {"port": 9876}}})
        self.assertFalse(result["integrations"]["blender"]["tcp_reachable"])
        self.assertFalse(result["integrations"]["blender"]["editor_verified"])

    def test_native_process_list_and_system_info(self):
        self.assertIn("workspace", bridge.system_info())
        self.assertLessEqual(bridge.process_list(bridge.ProcessListRequest(limit=3))["count"], 3)

    def test_portable_search_prunes_secrets_and_limits_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "private").mkdir()
            (root / "private/key").write_text("needle secret")
            (root / "public").write_text("needle visible")
            config = {"filesystem": {"denied_paths": [str(root / "private")]}}
            def check(value):
                return security.checked_path(root, config, value)
            result = portable.search_files(root, check, "needle")
            self.assertIn("visible", result["matches"])
            self.assertNotIn("secret", result["matches"])

    def test_real_mcp_stdio_from_different_directory(self):
        import asyncio
        import sys
        from mcp import Client
        from mcp.client.stdio import StdioServerParameters
        async def probe():
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                config = root / "config.json"
                config.write_text(json.dumps({"workspace": str(root), "filesystem": {
                    "denied_paths": [str(root / "private")], "read_only_paths": [str(config)]}}))
                params = StdioServerParameters(command=sys.executable,
                    args=["-B", str(Path(__file__).with_name("run_bridge.py")), "stdio"],
                    cwd=str(root), env={"BRIDGE_CONFIG": str(config)})
                async with Client(params, read_timeout_seconds=15) as client:
                    catalog = await client.list_tools()
                    self.assertEqual(len(catalog.tools), 20)
                    result = await client.call_tool("system_info", {})
                    self.assertFalse(result.is_error)
                    result = await client.call_tool("read_file", {"path": "../outside"})
                    self.assertTrue(result.is_error)
                    self.assertIn("outside workspace", str(result.content))
        asyncio.run(probe())
