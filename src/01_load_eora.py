"""
01_load_eora.py
================
Load the Eora26 2022 core matrices and build the gross-output and CO2 vectors.

Reads the raw Eora26 text files (placed in ../data/ ; see data/README.md for
how to obtain them) and writes compact .npy artifacts to ../results/cache/ for
the downstream stages.

File semantics (Eora26 documentation + index_readme):
  Eora26_2022_bp_T.txt  : 4915 x 4915 inter-industry transaction matrix Z.
                          Last row/col (index 4915) is the 'ROW TOTAL' aggregate;
                          the first 4914 are the real country-sector pairs.
  Eora26_2022_bp_FD.txt : 4915 x 1140 final demand (190 regions x 6 categories).
  Eora26_2022_bp_Q.txt  : 2728 x 4915 satellite stressor accounts. The clean
                          'I-GHG-CO2 emissions (Gg)' block spans label lines
                          10..64 (0-indexed rows 9..63), i.e. 55 stressor rows.
  labels_T.txt          : 4915 country-sector labels (country, country, type, sector)

Usage:
    python 01_load_eora.py
"""
import os
import numpy as np

N_FULL = 4914          # real country-sectors (drop the ROW TOTAL row/col)
CO2_ROWS = (9, 64)     # 0-indexed [start, end) of the I-GHG-CO2 block in Q

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
CACHE = os.path.join(os.path.dirname(__file__), "..", "results", "cache")
os.makedirs(CACHE, exist_ok=True)


def _path(name):
    return os.path.join(DATA, name)


def main():
    print("Loading T (large, ~277 MB) ...", flush=True)
    T = np.loadtxt(_path("Eora26_2022_bp_T.txt"), delimiter="\t", max_rows=N_FULL)
    T = T[:, :N_FULL]
    print("  T:", T.shape)

    print("Loading FD ...", flush=True)
    FD = np.loadtxt(_path("Eora26_2022_bp_FD.txt"), delimiter="\t", max_rows=N_FULL)
    print("  FD:", FD.shape)

    # Gross output: x = Z i + y_total   (standard IO accounting identity)
    y_total = FD.sum(axis=1)
    x_out = T.sum(axis=1) + y_total
    print("  gross output: min=%.3e max=%.3e" % (x_out.min(), x_out.max()))

    # CO2 satellite block -> direct emissions per sector (Gg)
    print("Loading Q CO2 block (rows %d..%d) ..." % CO2_ROWS, flush=True)
    rows = []
    with open(_path("Eora26_2022_bp_Q.txt")) as f:
        for i, line in enumerate(f):
            if i < CO2_ROWS[0]:
                continue
            if i >= CO2_ROWS[1]:
                break
            rows.append(np.fromstring(line, sep="\t")[:N_FULL])
    co2_direct = np.array(rows).sum(axis=0)
    print("  total global direct CO2: %.2f Gt" % (co2_direct.sum() / 1e6))

    # Labels
    labels = []
    with open(_path("labels_T.txt")) as f:
        for i, line in enumerate(f):
            if i >= N_FULL:
                break
            p = line.rstrip("\n").split("\t")
            labels.append((p[0], p[2] if len(p) > 2 else "", p[3] if len(p) > 3 else ""))

    np.save(os.path.join(CACHE, "T.npy"), T)
    np.save(os.path.join(CACHE, "FD.npy"), FD)
    np.save(os.path.join(CACHE, "x_out.npy"), x_out)
    np.save(os.path.join(CACHE, "co2_direct.npy"), co2_direct)
    import json
    json.dump(labels, open(os.path.join(CACHE, "labels_T.json"), "w"))
    print("Saved cache to", CACHE)


if __name__ == "__main__":
    main()
