#!/bin/bash

for file in inputs/*.gr; do
    name=$(basename "$file" .gr)
    python3 main.py "$file" "outputs/$name.vc" --stats
    echo "----------------------"
done
