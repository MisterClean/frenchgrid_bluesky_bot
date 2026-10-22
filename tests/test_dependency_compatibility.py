"""Exercise the installed SDK without credentials, network requests, or posting."""

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from atproto import Client, models

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bot.bluesky_bot import BlueskyBot


class DependencyCompatibilityTests(unittest.TestCase):
    def test_current_sdk_accepts_existing_post_and_unicode_link_facets(self):
        bot = BlueskyBot.__new__(BlueskyBot)
        bot.client = SimpleNamespace(
            me=SimpleNamespace(did="did:plc:example"),
            com=SimpleNamespace(atproto=SimpleNamespace(repo=Mock())),
        )
        text = "⚡ France — Electricity Maps"
        bot.create_post(text)
        payload = bot.client.com.atproto.repo.create_record.call_args.kwargs["data"]
        validated = models.ComAtprotoRepoCreateRecord.Data.model_validate(payload)
        self.assertEqual(validated.collection, "app.bsky.feed.post")
        facet = payload["record"]["facets"][0]
        encoded = text.encode("utf-8")
        self.assertEqual(
            encoded[facet["index"]["byteStart"] : facet["index"]["byteEnd"]],
            b"Electricity Maps",
        )

    def test_client_construction_does_not_require_login(self):
        self.assertIsNotNone(Client().com.atproto.repo.create_record)


if __name__ == "__main__":
    unittest.main()
