#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail
shopt -s inherit_errexit lastpipe

export LC_ALL=C.UTF-8

list_db_files() {
    pacman -Qlq \
        | sed 's,/$,,' \
        | sort
    # Exclude directories using sed ^^^:
}

list_all_files() {
    local ignored_dirs=(
        /boot
        /dev
        /home
        /tmp
        /proc
        /root
        /run
        /sys
        /var/cache
        /var/lib/docker
        /var/log
    )

    local args=()

    local dir
    for dir in ${ignored_dirs[@]+"${ignored_dirs[@]}"}; do
        args+=(-path "$dir" -prune -o)
    done

    unset 'args[-1]'
    find / -\( ${args[@]+"${args[@]}"} -\) -o -print | sort
}

comm -13 <( list_db_files ) <( list_all_files )
