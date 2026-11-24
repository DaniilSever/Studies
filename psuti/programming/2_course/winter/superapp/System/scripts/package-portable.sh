#!/usr/bin/env bash
set -euo pipefail

# Usage: bash scripts/package-portable.sh build-redos [destination]
# Package layout: <destination>/System/{superapp,superapp_*,assets/}
# Runtime SUPERAPP_ROOT is <destination>; System remains protected.
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
build_dir="${1:-build}"
if [[ "$build_dir" != /* ]]; then build_dir="$project_root/$build_dir"; fi
output_dir="${2:-$project_root/release/SuperApp}"
if [[ "$output_dir" != /* ]]; then output_dir="$project_root/$output_dir"; fi

mkdir -p "$output_dir/System/assets"
for executable in superapp superapp_terminal superapp_monitoring superapp_popup; do
    if [[ ! -f "$build_dir/$executable" ]]; then
        echo "Missing executable: $build_dir/$executable" >&2
        exit 1
    fi
    install -m 755 "$build_dir/$executable" "$output_dir/System/$executable"
done

for asset in folder-icon.png file-icon.png; do
    if [[ ! -f "$project_root/src/modules/assets/$asset" ]]; then
        echo "Missing asset: $asset" >&2
        exit 1
    fi
    install -m 644 "$project_root/src/modules/assets/$asset" "$output_dir/System/assets/$asset"
done

printf 'Portable package: %s\n' "$output_dir"
printf 'Run: "%s/System/superapp"\n' "$output_dir"
printf 'Note: target Linux must have compatible Qt and other shared libraries.\n'
