from __future__ import annotations

from pathlib import Path

import pytest

from project_dumper import updater


def test_update_executable_replaces_older_binary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    executable = tmp_path / "produm"
    executable.write_bytes(b"old")

    monkeypatch.setattr(updater.platform, "system", lambda: "Linux")
    monkeypatch.setattr(updater.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(updater.sys, "executable", str(executable))
    monkeypatch.setattr(
        updater,
        "_fetch_latest_release",
        lambda: {
            "tag_name": "v0.4.0",
            "assets": [
                {
                    "name": updater.LINUX_ASSET_NAME,
                    "browser_download_url": "https://example.test/produm",
                }
            ],
        },
    )

    def fake_download(download_url: str, destination: Path) -> None:
        assert download_url == "https://example.test/produm"
        destination.write_bytes(b"new")

    monkeypatch.setattr(updater, "_download_executable", fake_download)

    message = updater.update_executable("0.3.0")

    assert message == "Updated produm from 0.3.0 to v0.4.0."
    assert executable.read_bytes() == b"new"
    assert executable.stat().st_mode & 0o111


def test_update_executable_skips_current_release(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    executable = tmp_path / "produm"
    executable.write_bytes(b"current")

    monkeypatch.setattr(updater.platform, "system", lambda: "Linux")
    monkeypatch.setattr(updater.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(updater.sys, "executable", str(executable))
    monkeypatch.setattr(
        updater,
        "_fetch_latest_release",
        lambda: {
            "tag_name": "v0.3.0",
            "assets": [
                {
                    "name": updater.LINUX_ASSET_NAME,
                    "browser_download_url": "https://example.test/produm",
                }
            ],
        },
    )

    assert updater.update_executable("0.3.0") == "produm 0.3.0 is already up to date."
    assert executable.read_bytes() == b"current"


def test_update_rejects_python_install(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(updater.platform, "system", lambda: "Linux")
    monkeypatch.setattr(updater.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(updater.sys, "executable", "/usr/bin/python3")

    with pytest.raises(updater.UpdateError, match="standalone binary"):
        updater.update_executable("0.3.0")
