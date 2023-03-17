#!/usr/bin/env bash

# Copyright (c) 2023 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "audit-scripts" project.
# For details, see https://github.com/egor-tensin/audit-scripts.
# Distributed under the MIT License.

set -o errexit -o nounset -o pipefail
shopt -s inherit_errexit lastpipe

script_name="$( basename -- "${BASH_SOURCE[0]}" )"
readonly script_name

check_tool() {
    local tool
    for tool; do
        if ! command -v "$tool" > /dev/null; then
            echo "$script_name: $tool is missing" >&2
            exit 1
        fi
    done
}

print_usage() {
    echo "usage: $script_name [-h] [-6] [-p PORT_RANGES] [-t TOP_N_PORTS] HOST"
}

exit_with_usage_error() {
    local msg
    for msg; do
        echo "usage error: $msg" >&2
    done
    print_usage >&2
    exit 1
}

host=
declare -a nmap_args=()

parse_args() {
    local ports=
    local top_ports=

    local opt
    while getopts ':h6p:t:' opt; do
        case "$opt" in
            h)
                print_usage
                exit 0
                ;;
            6)
                nmap_args+=('-6')
                ;;
            p)
                ports="$OPTARG"
                ;;
            t)
                top_ports="$OPTARG"
                ;;
            :)
                exit_with_usage_error "option -$OPTARG requires an argument"
                ;;
            *)
                exit_with_usage_error "option -$OPTARG is invalid"
                ;;
        esac
    done
    shift "$((OPTIND - 1))"

    if [ "$#" -ne 1 ]; then
        exit_with_usage_error
    fi

    host="$1"

    if [ -n "$ports" ] && [ -n "$top_ports" ]; then
        exit_with_usage_error "you can't use both -p and -t options"
    fi
    if [ -z "$ports" ] && [ -z "$top_ports" ]; then
        ports='-'
    fi

    if [ -n "$ports" ]; then
        nmap_args+=('-p' "$ports")
    fi
    if [ -n "$top_ports" ]; then
        nmap_args+=('--top-ports' "$top_ports")
    fi
}

main() {
    check_tool nmap xmlstarlet
    parse_args "$@"

    nmap ${nmap_args[@]+"${nmap_args[@]}"} -oX - -- "$host" | xmlstarlet sel -t -v '//port[state/@state="open"]/@portid' -nl
}

main "$@"
