"""
03_build_subsystem.py
=====================
Aggregate the full 4914-sector Eora system into a real four-sector US-China
subsystem suitable for an actual HHL circuit, preserving the bilateral
structure. Every entry of the resulting 4x4 system is a genuine aggregate of
Eora data (real transaction flows, real gross output, real emission intensities,
real US final demand).

Macro-sectors:
  US-Energy, US-NonEnergy, CN-Energy, CN-NonEnergy
where Energy = {Mining and Quarrying, Electricity Gas and Water,
                Petroleum/Chemical/Non-Metallic Mineral Products, Transport}.

Output:
  results/sub4.npz  : A, M=(I-A), e, y, x, co2, groups, classical solution x_sol, E

Usage:
    python 03_build_subsystem.py
"""
import os
import json
import numpy as np

CACHE = os.path.join(os.path.dirname(__file__), "..", "results", "cache")
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
DATA = os.path.join(os.path.dirname(__file__), "..", "data")

ENERGY = {"Mining and Quarrying", "Electricity, Gas and Water",
          "Petroleum, Chemical and Non-Metallic Mineral Products", "Transport"}
GROUPS = ["US-Energy", "US-NonEnergy", "CN-Energy", "CN-NonEnergy"]


def macro(country, sector):
    grp = "Energy" if sector in ENERGY else "NonEnergy"
    if country == "USA":
        return "US-" + grp
    if country == "CHN":
        return "CN-" + grp
    return None


def main():
    T = np.load(os.path.join(CACHE, "T.npy"))
    x = np.load(os.path.join(CACHE, "x_out.npy"))
    co2 = np.load(os.path.join(CACHE, "co2_direct.npy"))
    FD = np.load(os.path.join(CACHE, "FD.npy"))
    labels = json.load(open(os.path.join(CACHE, "labels_T.json")))

    gidx = {g: [] for g in GROUPS}
    for i, (c, e, s) in enumerate(labels):
        m = macro(c, s)
        if m in gidx:
            gidx[m].append(i)

    k = len(GROUPS)
    Z = np.zeros((k, k)); xg = np.zeros(k); cg = np.zeros(k)
    for a, ga in enumerate(GROUPS):
        ia = gidx[ga]; xg[a] = x[ia].sum(); cg[a] = co2[ia].sum()
        for b, gb in enumerate(GROUPS):
            Z[a, b] = T[np.ix_(ia, gidx[gb])].sum()
    A = Z / xg[np.newaxis, :]
    cs = A.sum(axis=0)
    A = A * np.minimum(1.0, 0.95 / np.maximum(cs, 1e-9))[np.newaxis, :]
    e = cg / xg
    M = np.eye(k) - A

    fd_country = []
    with open(os.path.join(DATA, "labels_FD.txt")) as f:
        for i, line in enumerate(f):
            if i >= FD.shape[1]:
                break
            fd_country.append(line.split("\t")[0])
    fd_country = np.array(fd_country)
    yUS = FD[:, fd_country == "USA"].sum(axis=1); yUS[yUS < 0] = 0
    y = np.array([yUS[gidx[g]].sum() for g in GROUPS])

    x_sol = np.linalg.solve(M, y)
    E = e @ x_sol
    print("kappa(I-A) =", round(np.linalg.cond(M), 3))
    print("classical x =", np.round(x_sol, 3))
    print("E = %.4f Gt" % (E / 1e6))

    np.savez(os.path.join(RESULTS, "sub4.npz"),
             A=A, M=M, e=e, y=y, x=xg, co2=cg,
             groups=GROUPS, x_sol=x_sol, E=E)
    print("Saved sub4.npz")


if __name__ == "__main__":
    main()
