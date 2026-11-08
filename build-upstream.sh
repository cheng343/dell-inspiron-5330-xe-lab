#!/bin/bash
# Fetch public, pinned sources and invoke their existing builders. No installation.
set -euo pipefail
if [[ "$(uname -s)" != Darwin || "$(uname -m)" != x86_64 ]]; then
    echo 'Use an Intel macOS build runner.' >&2
    exit 2
fi
root=$(cd -- "$(dirname -- "$0")" && pwd)
cd "$root"
mkdir -p build
read_lock() { python3 -c 'import json,sys; print(json.load(open("UPSTREAM.lock.json"))[sys.argv[1]])' "$1"; }
upstream="$root/build/upstream"
source_commit=$(read_lock source_commit)
sdk_commit=$(read_lock sdk_commit)
fetch_pinned() {
    local path=$1 url=$2 commit=$3
    if [[ ! -d "$path/.git" ]]; then
        git init "$path"
        git -C "$path" remote add origin "$url"
    fi
    git -C "$path" fetch --depth 1 origin "$commit"
    git -C "$path" checkout --detach FETCH_HEAD
    [[ "$(git -C "$path" rev-parse HEAD)" == "$commit" ]]
    git -C "$path" diff --exit-code
}
fetch_pinned "$upstream" "$(read_lock source_repository)" "$source_commit"
deps="$upstream/build/deps"
mkdir -p "$deps"
fetch_pinned "$deps/MacKernelSDK" "$(read_lock sdk_repository)" "$sdk_commit"
curl -fL --retry 3 -o "$deps/lilu.zip" "$(read_lock lilu_archive_url)"
printf '%s  %s\n' "$(read_lock lilu_archive_sha256)" "$deps/lilu.zip" | shasum -a 256 -c -
unzip -qo "$deps/lilu.zip" -d "$deps"
test -f "$deps/Lilu.kext/Contents/Resources/Headers/kern_api.hpp"
{
    printf 'SourceCommit=%s\nSDKCommit=%s\n' "$source_commit" "$sdk_commit"
    printf 'LiluArchiveSHA256=%s\n' "$(read_lock lilu_archive_sha256)"
    sw_vers
    xcrun clang --version
} > build/source-state.txt
zsh "$upstream/build-nootedgreen.sh"
zsh "$upstream/build-hookcase.sh"
# Confirm that building did not modify tracked upstream driver sources.
git -C "$upstream" diff --exit-code
echo 'Upstream NootedGreen and HookCase built. No driver installed or loaded.'
