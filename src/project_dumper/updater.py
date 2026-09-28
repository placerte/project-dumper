from __future__ import annotations

import json
import os
import platform
import stat
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

LATEST_RELEASE_URL = (
    "https://api.github.com/repos/placerte/project-dumper/releases/latest"
)
LINUX_ASSET_NAME = "produm-linux-x86_64"


class UpdateError(RuntimeError):
    """Raised when the standalone executable cannot be updated safely."""


def _parse_version(version: str) -> tuple[int, ...]:
    normalized = version.removeprefix("v")
    try:
        return tuple(int(part) for part in normalized.split("."))
    except ValueError as exc:
        raise UpdateError(f"Unsupported release version: {version}") from exc


def _fetch_latest_release() -> dict[str, object]:
    request = urllib.request.Request(
        LATEST_RELEASE_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "produm-updater",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = response.read()
    except (OSError, urllib.error.URLError) as exc:
        raise UpdateError(f"Could not check GitHub releases: {exc}") from exc

    try:
        release = json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise UpdateError("GitHub returned an invalid release response") from exc
    if not isinstance(release, dict):
        raise UpdateError("GitHub returned an invalid release response")
    return release


def _get_release_asset(release: dict[str, object]) -> tuple[str, str]:
    tag = release.get("tag_name")
    assets = release.get("assets")
    if not isinstance(tag, str) or not isinstance(assets, list):
        raise UpdateError("Latest release metadata is incomplete")

    for asset in assets:
        if not isinstance(asset, dict) or asset.get("name") != LINUX_ASSET_NAME:
            continue
        download_url = asset.get("browser_download_url")
        if isinstance(download_url, str):
            return tag, download_url
    raise UpdateError(f"Latest release does not include {LINUX_ASSET_NAME}")


def _download_executable(download_url: str, destination: Path) -> None:
    request = urllib.request.Request(
        download_url,
        headers={"User-Agent": "produm-updater"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            destination.write_bytes(response.read())
    except (OSError, urllib.error.URLError) as exc:
        raise UpdateError(f"Could not download the update: {exc}") from exc


def update_executable(current_version: str) -> str:
    """Update the running standalone Linux executable from GitHub Releases."""
    # GitHub issue #1: provide a typical Linux release with self-update support.
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "amd64"}:
        raise UpdateError("Automatic updates support Linux x86_64 only")

    executable = Path(sys.executable).resolve()
    if executable.name not in {"produm", LINUX_ASSET_NAME}:
        raise UpdateError(
            "This command only updates the standalone binary; update Python "
            "installations with uv or pip"
        )

    release, download_url = _get_release_asset(_fetch_latest_release())
    if _parse_version(release) <= _parse_version(current_version):
        return f"produm {current_version} is already up to date."

    try:
        with tempfile.NamedTemporaryFile(
            dir=executable.parent,
            prefix=".produm-update-",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
        _download_executable(download_url, temporary_path)
        temporary_path.chmod(
            temporary_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )
        os.replace(temporary_path, executable)
    except OSError as exc:
        raise UpdateError(f"Could not replace {executable}: {exc}") from exc
    finally:
        if "temporary_path" in locals():
            temporary_path.unlink(missing_ok=True)

    return f"Updated produm from {current_version} to {release}."
