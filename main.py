from pathlib import Path
import argparse
import sys

from io_utils import read_gr, write_vc
from solver import solve_vertex_cover
from validator import validate_vertex_cover


def main() -> int:
    parser = argparse.ArgumentParser( # sukuriamas parser objektas argumentams
        description="Exact Minimum Vertex Cover solver using Branch and Bound."
    )

    parser.add_argument(
        "input_file",
        help="Input graph file in PACE .gr format",
    )

    parser.add_argument(
        "output_file",
        nargs="?", # neprivalomas arg
        help="Output solution file in PACE .vc format. If omitted, uses input name with .vc extension.",
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print Branch and Bound search statistics.",
    )

    args = parser.parse_args() # pasiema visus args ir priskiria args dictionary

    input_path = Path(args.input_file)

    if args.output_file:
        output_path = Path(args.output_file)
    else:
        output_path = input_path.with_suffix(".vc")

    n, edges = read_gr(input_path) # nuskaitomas grafas is gr failo

    cover, stats = solve_vertex_cover(n, edges) # apskaiciuojamas cover ir statistika

    is_valid, message = validate_vertex_cover(n, edges, cover) # validuojamas coveris
    if not is_valid:
        raise RuntimeError(f"Internal error: generated solution is invalid: {message}")

    write_vc(output_path, n, cover) # sprendinys irasomas i vc faila

    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"Minimum vertex cover size: {len(cover)}")
    print(f"Cover vertices: {' '.join(map(str, sorted(cover)))}")

    if args.stats:
        print()
        print("Search statistics")
        print("-----------------")
        print(f"Recursive calls:      {stats.recursive_calls}")
        print(f"Pruned by size:       {stats.pruned_by_size}")
        print(f"Pruned by lower bound:{stats.pruned_by_bound}")
        print(f"Safe reductions:      {stats.reductions_applied}")
        print(f"Time:                 {stats.elapsed_seconds:.6f} s")

    return 0


if __name__ == "__main__":
    sys.exit(main())
