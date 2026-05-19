from pathlib import Path


def _normalize_edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u <= v else (v, u)


def read_gr(path: str | Path) -> tuple[int, list[tuple[int, int]]]:
    path = Path(path)

    n = None # briaunu skaicius
    declared_m = None # faile deklaruotas briaunu skaicius
    raw_edge_count = 0 # perskaitytos briaunu eilutes
    edges: set[tuple[int, int]] = set() # unikalios briaunos

    with path.open("r", encoding="utf-8") as f:
        for line_nr, raw_line in enumerate(f, start=1):
            line = raw_line.strip()

            if not line:
                continue

            if line.startswith("c"):
                continue

            parts = line.split()

            if parts[0] == "p":
                if len(parts) != 4:
                    raise ValueError(
                        f"{path}:{line_nr}: Klaida, problemos eilute turi buti: p td <n> <m>"
                    )

                descriptor = parts[1]
                if descriptor != "td":
                    raise ValueError(
                        f"{path}:{line_nr}: Truksta deskriptoriaus 'td'"
                    )

                n = int(parts[2])
                declared_m = int(parts[3])

                if n < 0 or declared_m < 0:
                    raise ValueError(f"{path}:{line_nr}: n ir m turi buti neneigiami")

            else:
                if n is None:
                    raise ValueError(
                        f"{path}:{line_nr}: briauna parasyta pries problemos eilute"
                    )

                if len(parts) != 2:
                    raise ValueError(
                        f"{path}:{line_nr}: briauna turi tureti 2 skaicius"
                    )

                u = int(parts[0])
                v = int(parts[1])

                if not (1 <= u <= n and 1 <= v <= n):
                    raise ValueError(
                        f"{path}:{line_nr}: briaunos id turi buti tarp 1 ir {n}"
                    )

                raw_edge_count += 1
                edges.add(_normalize_edge(u, v))

    if n is None:
        raise ValueError(f"{path}: nera problemos eilut: p td <n> <m>")

    return n, sorted(edges) # grazinama briaunu kiekis ir briaunu sarasas (patogiau nei set)


def write_vc(path: str | Path, n: int, cover: set[int] | list[int]) -> None:

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    cover_sorted = sorted(set(cover))

    with path.open("w", encoding="utf-8") as f:
        f.write(f"s vc {n} {len(cover_sorted)}\n")
        for v in cover_sorted:
            f.write(f"{v}\n")
