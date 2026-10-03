#!/usr/bin/env bash
set -eu

config_dir=$(dirname -- "$(realpath -- "$0")")
exec clash-man --config "$config_dir/config.yaml" update --force
