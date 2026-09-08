"""Installer boundaries and preservation; no package downloads in unit tests."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import setup_bridge as installer


class LinuxInstallerTests(unittest.TestCase):
    def test_non_linux_rejected_before_changes(self):
        for system in ("Windows", "Darwin"):
            with self.subTest(system=system), patch.object(installer.platform, "system", return_value=system):
                with self.assertRaisesRegex(ValueError, "Linux"):
                    installer.require_linux()

    def test_root_and_wsl_rejected(self):
        with patch.object(installer.os, "geteuid", return_value=0):
            with self.assertRaisesRegex(ValueError, "sudo"):
                installer.require_linux()
        with patch.object(installer.os, "geteuid", return_value=1000), patch.object(installer.platform, "release", return_value="microsoft-standard-WSL2"):
            with self.assertRaisesRegex(ValueError, "WSL"):
                installer.require_linux()

    def test_invalid_workspace_does_not_install_packages(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(installer, "ROOT", Path(temp)), patch.object(installer.sys, "argv", ["setup_bridge.py", "--workspace", temp]), patch.object(installer.subprocess, "run") as run, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as exit:
                installer.main()
            self.assertEqual(exit.exception.code, 1)
            run.assert_not_called()

    def test_invalid_application_does_not_create_workspace(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "install"
            root.mkdir()
            workspace = Path(temp) / "projects"
            with patch.object(installer, "ROOT", root):
                with self.assertRaises(FileNotFoundError):
                    installer.configure(workspace, blender=str(root / "missing"))
            self.assertFalse(workspace.exists())
            self.assertFalse((root / ".local").exists())

    def test_home_and_overlapping_workspaces_rejected(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(installer, "ROOT", Path(temp) / "install"):
            for workspace in (Path.home(), Path('/'), installer.ROOT, installer.ROOT / 'projects', installer.ROOT.parent):
                with self.subTest(workspace=workspace), self.assertRaises(ValueError):
                    installer.build_config(workspace)

    def test_configuration_mode_0600(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'install'
            root.mkdir()
            with patch.object(installer, 'ROOT', root):
                installer.configure(Path(temp) / 'projects')
            self.assertEqual((root / 'bridge_config.json').stat().st_mode & 0o777, 0o600)

    def test_reinstallation_preserves_configuration_and_ignores_new_workspace(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'install'
            root.mkdir()
            with patch.object(installer, 'ROOT', root), contextlib.redirect_stdout(io.StringIO()):
                installer.configure(Path(temp) / 'projects')
                before = (root / 'bridge_config.json').read_bytes()
                other = Path(temp) / 'other'
                with patch.object(installer.sys, 'argv', ['setup_bridge.py', '--configure-only', '--workspace', str(other)]):
                    installer.main()
                self.assertEqual((root / 'bridge_config.json').read_bytes(), before)
                self.assertFalse(other.exists())

    def test_check_does_not_create_files(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(installer, 'ROOT', Path(temp)), patch.object(installer, 'preflight'), patch.object(installer.sys, 'argv', ['setup_bridge.py', '--check']), contextlib.redirect_stdout(io.StringIO()):
            installer.main()
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_mcp_json_handles_spaces_and_preserves_edits(self):
        with tempfile.TemporaryDirectory(prefix='linux installer ') as temp:
            root = Path(temp)
            (root / '.local').mkdir()
            blender = root / '.venv-blender/bin/python'
            blender.parent.mkdir(parents=True)
            blender.touch()
            with patch.object(installer, 'ROOT', root), contextlib.redirect_stdout(io.StringIO()):
                installer.export_client_config()
                path = root / '.local/mcp-client.json'
                config = json.loads(path.read_text())['mcpServers']
                self.assertEqual(config['pcbridge-linux']['args'], [str(root / 'run_bridge.py'), 'stdio'])
                self.assertEqual(config['blender-linux']['command'], str(blender))
                path.write_text('user settings')
                installer.export_client_config()
                self.assertEqual(path.read_text(), 'user settings')
