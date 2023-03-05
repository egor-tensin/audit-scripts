#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail
shopt -s inherit_errexit lastpipe

if ! command -v cruft &> /dev/null; then
    echo 'Where is cruft?' >&2
    exit 1
fi

ignored_dirs=(
    /boot
    /etc/letsencrypt
    /home
    /snap
    /srv
    /tmp
    /var/lib/docker
    /var/lib/i2pd
    /var/lib/snapd
    /var/lib/tor
    /var/log
)

args=()

for dir in ${ignored_dirs[@]+"${ignored_dirs[@]}"}; do
    args+=(--ignore "$dir")
done

cruft ${args[@]+"${args[@]}"}
