"""Reject invalid release metadata before touching installed code or services."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

SPEC = importlib.util.spec_from_file_location(
    "release_updater", Path(__file__).resolve().parents[1] / "deploy/update-release.py"
)
updater = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(updater)


class ReleaseValidationTests(unittest.TestCase):
    def test_invalid_release_identity_cannot_activate_code(self):
        with patch.object(updater.subprocess, "run", return_value=SimpleNamespace(returncode=0)), patch.object(
            updater, "download", return_value=b'{"tag_name":"production"}'
        ):
            with self.assertRaisesRegex(ValueError, "identity"):
                updater.update()

    def test_checksum_failure_does_not_create_a_release_directory(self):
        commit = "a" * 40
        prefix = f"https://github.com/MisterClean/frenchgrid_bluesky_bot/releases/download/build-{commit}/"
        release = {
            "tag_name": f"build-{commit}",
            "assets": [
                {"name": name, "browser_download_url": prefix + name}
                for name in ["manifest.json", "frenchgrid-bot.tar.gz"]
            ],
        }
        manifest = {"commit": commit, "sha256": "0" * 64}
        with tempfile.TemporaryDirectory() as directory, patch.object(
            updater, "RELEASES", Path(directory)
        ), patch.object(updater.subprocess, "run", return_value=SimpleNamespace(returncode=0)), patch.object(
            updater, "download", side_effect=[json.dumps(release).encode(), json.dumps(manifest).encode(), b"invalid"]
        ):
            with self.assertRaisesRegex(ValueError, "checksum"):
                updater.update()
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_response_size_is_bounded(self):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b"12345"
        with patch.object(updater.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex(ValueError, "size limit"):
                updater.download("https://api.github.com/example", 4)


if __name__ == "__main__":
    unittest.main()
