#!/usr/bin/env bash
set -e

mkdir -p outputs

for file in inputs/06_big_path_100.gr inputs/07_big_cycle_100.gr inputs/08_big_complete_bipartite_30_40.gr; do
    name=$(basename "$file" .gr)
    python3 main.py "$file" "outputs/$name.vc" --stats
    echo "----------------------"
done
