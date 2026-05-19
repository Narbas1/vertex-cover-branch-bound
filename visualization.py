from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt


INPUT_DIR = Path("inputs")
OUTPUT_DIR = Path("outputs")
IMAGE_DIR = Path("images")
IMAGE_DIR.mkdir(exist_ok=True)


def read_gr(path):
    n = None
    edges = set()

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("c"):
                continue

            parts = line.split()

            if parts[0] == "p":
                n = int(parts[2])
            else:
                u = int(parts[0])
                v = int(parts[1])
                edge = (u, v) if u <= v else (v, u)
                edges.add(edge)

    return n, sorted(edges)


def read_vc(path):
    cover = set()

    with path.open("r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    for line in lines[1:]:
        cover.add(int(line))

    return cover


# Rankiniu būdu parinktos pozicijos, kad maži grafai atrodytų tvarkingai
POSITIONS = {
    "01_path": {
        1: (0, 0),
        2: (1, 0),
        3: (2, 0),
    },
    "02_triangle": {
        1: (1, 1),
        2: (0, 0),
        3: (2, 0),
    },
    "03_cycle4": {
        1: (0, 1),
        2: (1, 1),
        3: (1, 0),
        4: (0, 0),
    },
    "04_disconnected": {
        1: (0, 0),
        2: (1, 0),
        3: (2, 0),
        4: (4, 0),
        5: (5, 0),
        6: (7, 0),  # izoliuota viršūnė
    },
    "05_loop_duplicate_isolated": {
        1: (0, 1),
        2: (1, 1),
        3: (2, 1),
        4: (1, 0),
        5: (3.5, 0.5),  # izoliuota arba atskira pagal tavo testą
    },
}


def draw_graph(input_file, output_file):
    n, edges = read_gr(input_file)
    cover = read_vc(output_file)

    G = nx.Graph()
    G.add_nodes_from(range(1, n + 1))
    G.add_edges_from(edges)

    stem = input_file.stem.replace(".gr", "")
    short_name = stem.split("_", 1)[0] + "_" + stem.split("_", 2)[1] if "_" in stem else stem

    # Bandome paimti rankines pozicijas pagal pirmą failo dalį
    if input_file.stem.startswith("01_path"):
        pos = POSITIONS["01_path"]
    elif input_file.stem.startswith("02_triangle"):
        pos = POSITIONS["02_triangle"]
    elif input_file.stem.startswith("03_cycle4"):
        pos = POSITIONS["03_cycle4"]
    elif input_file.stem.startswith("04_disconnected"):
        pos = POSITIONS["04_disconnected"]
    elif input_file.stem.startswith("05_loop_duplicate_isolated"):
        pos = POSITIONS["05_loop_duplicate_isolated"]
    else:
        pos = nx.spring_layout(G, seed=42)

    node_colors = []
    for node in G.nodes():
        if node in cover:
            node_colors.append("orange")
        else:
            node_colors.append("lightblue")

    plt.figure(figsize=(6, 4))
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color=node_colors,
        node_size=900,
        font_size=11,
        edgecolors="black",
        width=2,
    )

    plt.title(f"{input_file.stem}\nPažymėtas viršūnių denginys", fontsize=11)
    plt.tight_layout()

    out_path = IMAGE_DIR / f"{input_file.stem}.png"
    plt.savefig(out_path, dpi=200)
    plt.close()

    print(f"Išsaugota: {out_path}")


def main():
    small_tests = [
        "01_path.gr",
        "02_triangle.gr",
        "03_cycle4.gr",
        "04_disconnected.gr",
        "05_loop_duplicate_isolated.gr",
    ]

    for filename in small_tests:
        input_file = INPUT_DIR / filename
        output_file = OUTPUT_DIR / filename.replace(".gr", ".vc")

        if not input_file.exists():
            print(f"Nerastas input: {input_file}")
            continue

        if not output_file.exists():
            print(f"Nerastas output: {output_file}")
            continue

        draw_graph(input_file, output_file)


if __name__ == "__main__":
    main()