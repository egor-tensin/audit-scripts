#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail
shopt -s inherit_errexit lastpipe

if ! command -v debsums &> /dev/null; then
    echo 'Where is debsums?' >&2
    exit 1
fi

debsums -ca
