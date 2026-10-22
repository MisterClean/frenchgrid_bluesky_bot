#!/usr/bin/env python3
"""Install the latest tested, checksummed release without inbound CI SSH."""

import fcntl
import hashlib
import json
import re
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path

RELEASES = Path("/opt/frenchgrid-bot/releases")
API = "https://api.github.com/repos/MisterClean/frenchgrid_bluesky_bot/releases/latest"
MAX_ARCHIVE_BYTES = 5 * 1024 * 1024


def download(url: str, limit: int) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "frenchgrid-release-updater"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Release response exceeds its size limit")
    return data


def update() -> None:
    if subprocess.run(
        ["systemctl", "is-enabled", "--quiet", "frenchgrid-bot.service"], check=False
    ).returncode != 0:
        raise RuntimeError("Complete the initial service migration before enabling updates")
    release = json.loads(download(API, 1024 * 1024))
    tag = release["tag_name"]
    if not re.fullmatch(r"build-[0-9a-f]{40}", tag):
        raise ValueError("Unexpected release identity")
    commit = tag.removeprefix("build-")
    assets = {asset["name"]: asset["browser_download_url"] for asset in release["assets"]}
    expected_prefix = f"https://github.com/MisterClean/frenchgrid_bluesky_bot/releases/download/{tag}/"
    for name in ["manifest.json", "frenchgrid-bot.tar.gz"]:
        if assets[name] != expected_prefix + name:
            raise ValueError("Unexpected release asset location")
    manifest = json.loads(download(assets["manifest.json"], 8192))
    if manifest["commit"] != commit or not re.fullmatch(r"[0-9a-f]{64}", manifest["sha256"]):
        raise ValueError("Release manifest identity is invalid")
    destination = RELEASES / commit
    current = Path("/opt/frenchgrid-bot/current")
    if current.is_symlink() and current.resolve() == destination and (destination / ".complete").is_file():
        return
    archive = download(assets["frenchgrid-bot.tar.gz"], MAX_ARCHIVE_BYTES)
    if hashlib.sha256(archive).hexdigest() != manifest["sha256"]:
        raise ValueError("Release checksum mismatch")
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile() as source:
        source.write(archive)
        source.seek(0)
        with tarfile.open(fileobj=source, mode="r:gz") as bundle:
            members = bundle.getmembers()
            if sum(member.size for member in members) > 20 * 1024 * 1024:
                raise ValueError("Expanded release exceeds its size limit")
            if any(not (member.isfile() or member.isdir()) for member in members):
                raise ValueError("Release must contain only regular files and directories")
            bundle.extractall(destination, members=members, filter="data")
    subprocess.run(
        ["bash", str(destination / "deploy/install-service"), commit, "--activate"], check=True
    )
    print(f"Activated tested release {commit}")


if __name__ == "__main__":
    with Path("/opt/frenchgrid-bot/update.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        update()
