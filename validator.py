def validate_vertex_cover(
    n: int,
    edges: list[tuple[int, int]] | set[tuple[int, int]],
    cover: set[int] | list[int],
) -> tuple[bool, str]:

    cover_set = set(cover)

    for v in cover_set:
        if v < 1 or v > n:
            return False, f"Virsune {v} intervalo isoreje 1..{n}"

    for u, v in edges:
        if u not in cover_set and v not in cover_set:
            return False, f"Briauna ({u}, {v}) nepadengta"

    return True, "OK"
