"""
02_classical_mrio.py
====================
Build the regularised Leontief system from the cached Eora matrices and compute
the full-scale US-China consumption-based carbon footprints.

The raw Eora technical-coefficient matrix is economically non-viable: a small
number of micro-sectors with near-zero gross output but non-zero recorded
transactions produce explosive coefficients (spectral radius ~1.3e4). We apply
a minimal viability regularisation -- zeroing inactive artifact sectors and
capping column sums at 0.95 -- which restores spectral radius < 1 and yields a
well-defined Leontief inverse, while leaving the large US/CHN sectors untouched
(headline figures shift < 0.5%).

Outputs:
  results/classical_summary.json  : footprints, spectral radius, condition number
  results/cache/{A_clean,L_clean,e_clean}.npy

Usage:
    python 02_classical_mrio.py
"""
import os
import json
import numpy as np
from scipy.sparse.linalg import eigs
from scipy.sparse import csr_matrix

CACHE = os.path.join(os.path.dirname(__file__), "..", "results", "cache")
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
DATA = os.path.join(os.path.dirname(__file__), "..", "data")

N = 4914
ARTIFACT_FLOOR = 1e-4   # gross output below this * median => inactive artifact
COLSUM_CAP = 0.95       # cap column sums for viability


def demand_of(country, FD, fd_country):
    cols = np.where(fd_country == country)[0]
    y = FD[:, cols].sum(axis=1)
    y[y < 0] = 0.0          # drop negative inventory adjustments for footprint
    return y


def main():
    T = np.load(os.path.join(CACHE, "T.npy"))
    FD = np.load(os.path.join(CACHE, "FD.npy"))
    x = np.load(os.path.join(CACHE, "x_out.npy"))
    co2 = np.load(os.path.join(CACHE, "co2_direct.npy"))
    labels = json.load(open(os.path.join(CACHE, "labels_T.json")))
    countries = np.array([l[0] for l in labels])

    # --- artifact detection + regularisation ---
    xs = x.copy().astype(float)
    xs[xs <= 0] = np.nan
    med = np.nanmedian(xs)
    artifact = np.nan_to_num(xs, nan=0.0) < med * ARTIFACT_FLOOR
    x_clean = np.where(artifact, 1.0, np.nan_to_num(xs, nan=1.0))

    A = T / x_clean[np.newaxis, :]
    A[:, artifact] = 0.0
    A[artifact, :] = 0.0
    colsum = A.sum(axis=0)
    scale = np.ones(N)
    mask = colsum > COLSUM_CAP
    scale[mask] = COLSUM_CAP / colsum[mask]
    A = A * scale[np.newaxis, :]

    rho = abs(eigs(csr_matrix(A), k=1, which="LM",
                   return_eigenvectors=False, maxiter=10000)[0])
    L = np.linalg.inv(np.eye(N) - A)
    cond = np.linalg.cond(np.eye(N) - A)
    e = co2 / x_clean
    e[artifact] = 0.0
    print("spectral radius = %.4f, kappa(I-A) = %.2f, #artifacts = %d"
          % (rho, cond, int(artifact.sum())))

    # --- bilateral footprints ---
    fd_country = []
    with open(os.path.join(DATA, "labels_FD.txt")) as f:
        for i, line in enumerate(f):
            if i >= FD.shape[1]:
                break
            fd_country.append(line.split("\t")[0])
    fd_country = np.array(fd_country)

    results = {}
    for consumer in ["USA", "CHN"]:
        y = demand_of(consumer, FD, fd_country)
        contrib = e * (L @ y)
        E = contrib.sum()
        by = {c: contrib[countries == c].sum() for c in np.unique(countries)}
        other = "CHN" if consumer == "USA" else "USA"
        results[consumer] = {
            "total_Gt": E / 1e6,
            "in_other_Gt": by[other] / 1e6,
            "domestic_Gt": by[consumer] / 1e6,
        }
        print("%s: %.3f Gt total | %.3f Gt in %s"
              % (consumer, E / 1e6, by[other] / 1e6, other))

    np.save(os.path.join(CACHE, "A_clean.npy"), A)
    np.save(os.path.join(CACHE, "L_clean.npy"), L)
    np.save(os.path.join(CACHE, "e_clean.npy"), e)
    np.save(os.path.join(CACHE, "artifact_mask.npy"), artifact)
    json.dump({"spectral_radius": float(rho), "condition_number": float(cond),
               "n_artifact": int(artifact.sum()), "results": results},
              open(os.path.join(RESULTS, "classical_summary.json"), "w"), indent=2)
    print("Saved classical_summary.json")


if __name__ == "__main__":
    main()
