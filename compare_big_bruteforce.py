from itertools import combinations
from pathlib import Path
import time

from io_utils import read_gr
from solver import solve_vertex_cover
from validator import validate_vertex_cover


BIG_TESTS = [
    "06_big_path_100.gr",
    "07_big_cycle_100.gr",
    "08_big_complete_bipartite_30_40.gr",
]

TIMEOUT_SECONDS = 1200.0


def brute_force_with_timeout(n, edges, timeout_seconds):
    vertices = list(range(1, n + 1)) # visu virsuniu sarasas
    start = time.perf_counter()
    checked = 0

    for size in range(n + 1): # einama per visus poaibiu dydzius
        for candidate in combinations(vertices, size): # gerenuojami visi poaibiai su konkreciu dydziu
            checked += 1

            elapsed = time.perf_counter() - start
            if elapsed >= timeout_seconds:
                return None, elapsed, checked, "TIMEOUT"

            cover = set(candidate)
            is_valid, _ = validate_vertex_cover(n, edges, cover)

            if is_valid:
                return cover, elapsed, checked, "FOUND"

    elapsed = time.perf_counter() - start
    return set(), elapsed, checked, "FOUND"


def format_big_number(x):
    return f"{x:.3e}"


def main():
    print(
        "Testas,n,m,Visi poaibiai,Brute force statusas,"
        "Brute force patikrinta,Brute force laikas,"
        "B&B dydis,B&B laikas,B&B rekursiniai kvietimai"
    )

    for filename in BIG_TESTS:
        input_path = Path("inputs") / filename

        n, edges = read_gr(input_path)
        m = len(edges)

        total_subsets = 2 ** n

        brute_cover, brute_time, checked, status = brute_force_with_timeout(
            n, edges, TIMEOUT_SECONDS
        )

        bb_cover, stats = solve_vertex_cover(n, edges)

        print(
            f"{filename},"
            f"{n},"
            f"{m},"
            f"{format_big_number(total_subsets)},"
            f"{status},"
            f"{checked},"
            f"{brute_time:.6f},"
            f"{len(bb_cover)},"
            f"{stats.elapsed_seconds:.6f},"
            f"{stats.recursive_calls}"
        )


if __name__ == "__main__":
    main()