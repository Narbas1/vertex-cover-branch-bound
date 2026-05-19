from __future__ import annotations

from dataclasses import dataclass
import time


@dataclass
class SearchStats:
    recursive_calls: int = 0
    pruned_by_size: int = 0
    pruned_by_bound: int = 0
    reductions_applied: int = 0
    start_time: float = 0.0
    end_time: float = 0.0

    @property
    def elapsed_seconds(self) -> float:
        return self.end_time - self.start_time

# (u, v) ir (v, u) pasidaro tapati briauna (u, v), taipogi u <= v
def normalize_edges(edges: list[tuple[int, int]] | set[tuple[int, int]]) -> set[tuple[int, int]]:
    normalized = set()
    for u, v in edges:
        normalized.add((u, v) if u <= v else (v, u))
    return normalized

# virsunes kurios yra incident pasirinktai briaunai yra pasalinamos, nes tampa padengtos. grazinamos nepasalintos briaunos
def remove_incident_edges(edges: set[tuple[int, int]], vertex: int) -> set[tuple[int, int]]:
    return {(u, v) for (u, v) in edges if u != vertex and v != vertex}

# padaro kaimynu ir laipsniu dictionaries
def build_adjacency(edges: set[tuple[int, int]]) -> tuple[dict[int, set[int]], dict[int, int]]:

    adj: dict[int, set[int]] = {} # kaimynai
    degree: dict[int, int] = {} # virsunes laipsnis

    for u, v in edges:
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)

        if u == v:
            degree[u] = degree.get(u, 0) + 1
        else:
            degree[u] = degree.get(u, 0) + 1
            degree[v] = degree.get(v, 0) + 1

    return adj, degree

# branch and bound reikia tureti pakankamai gera pradini sprendini, sitoj funkcijoj gaunamas geras
# bet nebutinai optimalus sprendinys. suzinome upperbound
def greedy_upper_bound(edges: set[tuple[int, int]]) -> set[int]:
    remaining = set(edges) # dar nepadengtos briaunos
    cover: set[int] = set() # pasirinktos virsunes

    while remaining:
        adj, degree = build_adjacency(remaining)
        chosen = max(degree, key=lambda v: degree[v]) # pasirenkame virsune su didziausiu laipsniu
        cover.add(chosen) # idedame ta virsune i dengini
        remaining = remove_incident_edges(remaining, chosen) # pasalinamos visos briaunos kurios liecia pasirinkta virsune

    return cover # grazinamas validus bet nebutinai minimalus denginys

# suskaiciuoja kiek yra matching briaunu (briaunu kurios nesidalina virsunemis su kitomis), is to gaunamas min skaicius
# uz kuri geresnio sprendinio nera
# kitaip sakant, maziausias imanomas sprendinys yra toks pat kiek yra nesikertanciu briaunu
def maximal_matching_lower_bound(edges: set[tuple[int, int]]) -> int:
    used_vertices: set[int] = set()
    matching_size = 0

    for u, v in sorted(edges):
        if u not in used_vertices and v not in used_vertices:
            matching_size += 1
            used_vertices.add(u)
            used_vertices.add(v)

    return matching_size


def apply_safe_reductions( # supaprastiname grafa, jeigu imanoma, pagrindiniam algoritmui maziau saku reikes tikrinti
    edges: set[tuple[int, int]],
    cover: set[int],
    best_size: int,
    stats: SearchStats,
) -> tuple[set[tuple[int, int]], set[int]]:

    remaining = set(edges)
    current_cover = set(cover)

    changed = True
    while changed:
        changed = False

        # randamos kilpos
        loop_vertices = {u for (u, v) in remaining if u == v}
        if loop_vertices: # jeigu yra kilpu, idedame i dengini ir pasaliname incident briaunas
            for v in loop_vertices:
                if v not in current_cover:
                    current_cover.add(v)
                    stats.reductions_applied += 1
                remaining = remove_incident_edges(remaining, v)
                changed = True

            if len(current_cover) >= best_size:
                return remaining, current_cover

            continue

        # Rule 2: degree-one vertices.
        adj, degree = build_adjacency(remaining)

        leaf = None
        for v, d in degree.items(): # randami lapai (virsunes su laipsniu 1)
            if d == 1:
                leaf = v
                break

        if leaf is not None: # lapo kaimyna idedame i cover
            neighbor = next(iter(adj[leaf]))

            if neighbor not in current_cover:
                current_cover.add(neighbor)
                stats.reductions_applied += 1

            remaining = remove_incident_edges(remaining, neighbor)
            changed = True

            if len(current_cover) >= best_size:
                return remaining, current_cover

    return remaining, current_cover # graziname sumazinta briaunu rinkini ir papildyta coveri


def choose_branch_edge(edges: set[tuple[int, int]]) -> tuple[int, int]: # pasirenka briauna, kurios galai turi didziausia laipsni
    _, degree = build_adjacency(edges)

    return max(
        edges,
        key=lambda edge: (
            degree.get(edge[0], 0) + degree.get(edge[1], 0),
            max(degree.get(edge[0], 0), degree.get(edge[1], 0)),
        ),
    )


def solve_vertex_cover( # branch and bounds main algo
    n: int,
    edges: list[tuple[int, int]] | set[tuple[int, int]],
) -> tuple[set[int], SearchStats]:

    stats = SearchStats(start_time=time.perf_counter()) # statistikos objektas sukuriamas

    initial_edges = normalize_edges(edges) # normalizuojame briaunas

    forced_cover: set[int] = set()
    initial_edges, forced_cover = apply_safe_reductions( # bandoma supaprastinti grafa pagal 2 taisykles
        initial_edges,
        forced_cover,
        best_size=10**18,
        stats=stats,
    )
    # aibiu sajunga su priverstinai pasirinktomis virsunemis (kilpos, lapu kaimynai) ir greedy sprendinio
    # kitaip tariant jeigu randamas sprendinys toks pat arba didesnis, reikia toliau toje sakoje neapsimoka tikrinti
    best_cover = forced_cover | greedy_upper_bound(initial_edges)

    def search(remaining_edges: set[tuple[int, int]], current_cover: set[int]) -> None:
        nonlocal best_cover

        stats.recursive_calls += 1

        remaining_edges, current_cover = apply_safe_reductions(
            remaining_edges,
            current_cover,
            best_size=len(best_cover),
            stats=stats,
        )

        if not remaining_edges: # nebera briaunu
            if len(current_cover) < len(best_cover):
                best_cover = set(current_cover)
            return

        if len(current_cover) >= len(best_cover): # jeigu pasirinkta tiek pat arba daugiau virsuniu nei esamas best cover. returninama
            stats.pruned_by_size += 1
            return

        lower_bound = maximal_matching_lower_bound(remaining_edges)
        if len(current_cover) + lower_bound >= len(best_cover): # griztame nes sioje sakoje nebeapsimoka toliau ieskoti
            stats.pruned_by_bound += 1
            return
        # jeigu  negrizome, reiskiasi reikia sakotis
        u, v = choose_branch_edge(remaining_edges) # pasirenkame nepadengta briauna

        _, degree = build_adjacency(remaining_edges) # gaunami laipsniai

        branch_vertices = sorted( # nusprendziamas saku eiliskumas pagal laipsni (didesnis - pirmesnis)
            [u, v],
            key=lambda vertex: degree.get(vertex, 0),
            reverse=True,
        )

        for vertex in branch_vertices:
            next_cover = set(current_cover)
            next_cover.add(vertex)

            next_edges = remove_incident_edges(remaining_edges, vertex)

            search(next_edges, next_cover)

    search(initial_edges, forced_cover)

    stats.end_time = time.perf_counter()
    return best_cover, stats
