#!/bin/sh
set -eu

# GitHub issue #1: install the standalone Linux release with one command.
repository="placerte/project-dumper"
asset_name="produm-linux-x86_64"
install_dir="${INSTALL_DIR:-${HOME}/.local/bin}"
install_path="${install_dir}/produm"

case "$(uname -s)-$(uname -m)" in
    Linux-x86_64|Linux-amd64) ;;
    *)
        echo "produm: the standalone release supports Linux x86_64 only" >&2
        exit 1
        ;;
esac

if ! command -v curl >/dev/null 2>&1; then
    echo "produm: curl is required" >&2
    exit 1
fi

mkdir -p "${install_dir}"
temporary_file="$(mktemp "${install_dir}/.produm.XXXXXX")"
trap 'rm -f "${temporary_file}"' EXIT HUP INT TERM

download_url="https://github.com/${repository}/releases/latest/download/${asset_name}"
curl -fL --retry 3 --output "${temporary_file}" "${download_url}"
chmod 0755 "${temporary_file}"
mv "${temporary_file}" "${install_path}"
trap - EXIT HUP INT TERM

echo "Installed produm to ${install_path}"
case ":${PATH}:" in
    *":${install_dir}:"*) ;;
    *) echo "Add ${install_dir} to PATH to run produm." ;;
esac
