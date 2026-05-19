from itertools import combinations
from pathlib import Path
import time

from io_utils import read_gr
from solver import solve_vertex_cover
from validator import validate_vertex_cover

SMALL_TESTS = [
    "01_path.gr",
    "02_triangle.gr",
    "03_cycle4.gr",
    "04_disconnected.gr",
    "05_loop_duplicate_isolated.gr",
]


def brute_force_vertex_cover(n, edges):

    vertices = list(range(1, n + 1))

    for size in range(n + 1):
        for candidate in combinations(vertices, size):
            cover = set(candidate)

            is_valid, _ = validate_vertex_cover(n, edges, cover)
            if is_valid:
                return cover

    return set()


def main():
    print(
        "Testas,n,m,Brute force dydis,Brute force laikas,Branch and Bound dydis,Branch and Bound laikas,Rekursiniai kvietimai")

    for filename in SMALL_TESTS:
        input_path = Path("inputs") / filename

        n, edges = read_gr(input_path)
        m = len(edges)

        # Brute force
        start = time.perf_counter()
        brute_cover = brute_force_vertex_cover(n, edges)
        brute_time = time.perf_counter() - start

        # Branch and Bound
        bb_cover, stats = solve_vertex_cover(n, edges)

        print(
            f"{filename},"
            f"{n},"
            f"{m},"
            f"{len(brute_cover)},"
            f"{brute_time:.6f},"
            f"{len(bb_cover)},"
            f"{stats.elapsed_seconds:.6f},"
            f"{stats.recursive_calls}"
        )


if __name__ == "__main__":
    main()