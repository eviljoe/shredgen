#!/bin/bash

shopt -s globstar
set -u
set -o pipefail


source="${BASH_SOURCE[0]}"

# resolve ${source} until the file is no longer a symlink
while [ -h "${source}" ]; do
  dir="$( cd -P "$( dirname "${source}" )" && pwd )"
  source="$(readlink "${source}")"
  # if ${source} was a relative symlink, we need to resolve it relative to the path where the symlink file was located
  [[ ${source} != /* ]] && source="${dir}/${source}"
done
dir="$( cd -P "$( dirname "${source}" )" && pwd )"

cd "${dir}/../src"

pipenv run mamba **.spec.py
