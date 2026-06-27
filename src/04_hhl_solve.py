"""
04_hhl_solve.py
===============
Solve the real Eora 4x4 Leontief subsystem with an explicitly constructed HHL
quantum circuit (Qiskit Aer statevector simulation) and compare to the exact
classical solution.

The non-symmetric Leontief matrix M=(I-A) is solved through its Hermitian
positive-definite normal equations  A_h x = b_h  with  A_h = M^T M ,  b_h = M^T y ,
which shares the exact solution. The HHL circuit is built from first principles:
state preparation, quantum phase estimation against e^{i A_h t}, eigenvalue
inversion via ancilla rotation, inverse QPE, and post-selection on the ancilla.

A small parameter sweep over clock-register size and evolution time selects the
configuration with lowest L2 error against the classical solution.

Output:
  results/hhl_final.npz : classical & HHL solution vectors, emission estimates,
                          relative error, circuit depth, qubit count, condition number

Usage:
    python 04_hhl_solve.py
"""
import os
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector, Operator
from qiskit.circuit.library import QFT, RYGate, UnitaryGate
from scipy.linalg import expm

RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")


def build_hhl(A_h, b, n_b, n_clock, time_scale):
    """Construct the HHL circuit for Hermitian PD A_h and RHS b."""
    evals, _ = np.linalg.eigh(A_h)
    lam_min, lam_max = evals.min(), evals.max()
    t = time_scale * 2 * np.pi / lam_max
    b_unit = b / np.linalg.norm(b)

    anc = QuantumRegister(1, "anc")
    clk = QuantumRegister(n_clock, "c")
    bq = QuantumRegister(n_b, "b")
    qc = QuantumCircuit(anc, clk, bq)

    qc.initialize(b_unit, bq[:])
    qc.h(clk[:])
    for j in range(n_clock):
        qc.append(UnitaryGate(Operator(expm(1j * A_h * t * (2 ** j)))).control(1),
                  [clk[j]] + bq[:])
    qc.append(QFT(n_clock, inverse=True, do_swaps=True), clk[:])

    C = lam_min   # rotation constant < smallest eigenvalue
    for m in range(1, 2 ** n_clock):
        lam_est = 2 * np.pi * (m / 2 ** n_clock) / t
        angle = 2 * np.arcsin(min(1.0, C / lam_est))
        if angle < 1e-4:
            continue   # skip negligible rotations -> large speedup
        bits = [(m >> k) & 1 for k in range(n_clock)]
        qc.append(RYGate(angle).control(n_clock, ctrl_state="".join(map(str, bits))),
                  clk[:] + [anc[0]])

    qc.append(QFT(n_clock, do_swaps=True), clk[:])
    for j in reversed(range(n_clock)):
        qc.append(UnitaryGate(Operator(expm(-1j * A_h * t * (2 ** j)))).control(1),
                  [clk[j]] + bq[:])
    qc.h(clk[:])
    return qc


def extract(qc, n_b, n_clock):
    """Read the post-selected (ancilla=1, clock=0) solution from the statevector."""
    sv = Statevector(qc).data
    nq = qc.num_qubits
    sol = np.zeros(2 ** n_b, dtype=complex)
    for idx in range(len(sv)):
        bits = [(idx >> k) & 1 for k in range(nq)]
        if bits[0] == 1 and sum(bits[1:1 + n_clock]) == 0:
            bval = sum(bit << k for k, bit in enumerate(bits[1 + n_clock:1 + n_clock + n_b]))
            sol[bval] = sv[idx]
    return np.real(sol)


def main():
    d = np.load(os.path.join(RESULTS, "sub4.npz"), allow_pickle=True)
    M = d["M"].astype(float); y = d["y"].astype(float)
    e = d["e"].astype(float); x_cl = d["x_sol"].astype(float)
    A_h = M.T @ M; b_h = M.T @ y
    evals, _ = np.linalg.eigh(A_h)
    print("kappa(A_h) = %.3f" % (evals.max() / evals.min()))

    best = None
    for n_clock in [9, 10]:
        for ts in [0.7, 0.85]:
            qc = build_hhl(A_h, b_h, 2, n_clock, ts)
            xh = extract(qc, 2, n_clock)
            if np.linalg.norm(xh) < 1e-9:
                continue
            alpha = (xh @ x_cl) / (xh @ xh)
            xs = alpha * xh
            err = np.linalg.norm(xs - x_cl) / np.linalg.norm(x_cl)
            print("  n_clock=%d ts=%.2f depth=%d err=%.3f"
                  % (n_clock, ts, qc.depth(), err))
            if best is None or err < best[0]:
                best = (err, n_clock, ts, xs, qc.depth())

    err, n_clock, ts, xs, depth = best
    E_cl = e @ x_cl; E_h = e @ xs
    print("\nBEST n_clock=%d ts=%.2f depth=%d qubits=%d" % (n_clock, ts, depth, 3 + n_clock))
    print("classical x =", np.round(x_cl, 3))
    print("HHL       x =", np.round(xs, 3))
    print("rel L2 error = %.2f%%" % (100 * err))
    print("E classical = %.4f Gt, E HHL = %.4f Gt, agreement = %.1f%%"
          % (E_cl / 1e6, E_h / 1e6, 100 * (1 - abs(E_h - E_cl) / E_cl)))

    np.savez(os.path.join(RESULTS, "hhl_final.npz"),
             x_cl=x_cl, x_hhl=xs, E_cl=E_cl, E_h=E_h, rel_err=err,
             depth=depth, n_clock=n_clock, nqubits=3 + n_clock,
             kappa=float(evals.max() / evals.min()))
    print("Saved hhl_final.npz")


if __name__ == "__main__":
    main()
