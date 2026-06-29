## Overview

This repository contains the full pipeline, data instructions, and results, testing the MRIO-HHL algorithm on a real consumption-based accounting problem.

| Quantity | Value |
|---|---|
| US consumption-based CO₂ footprint (full Eora26) | **6.44 Gt** |
| CHN consumption-based CO₂ footprint (full Eora26) | **8.27 Gt** |
| CO₂ emitted in CHN to satisfy US demand | **0.47 Gt** |
| CO₂ emitted in US to satisfy CHN demand | **0.08 Gt** |
| Carbon-leakage asymmetry ratio | **6.2×** |
| Full-system Leontief condition number κ (regularised) | **≈ 35** |
| HHL vs classical solution (4-sector subsystem), rel. L2 error | **4.3 %** |
| HHL vs classical embodied-emission estimate, agreement | **86.7 %** |
| HHL circuit | 12 qubits, depth 533 |

---

## Repository layout

```
mrio-hhl-us-china-ext/
├── README.md
├── LICENSE
├── requirements.txt
├── Makefile
├── .gitignore
├── data/
│   └── README.md            # how to obtain the Eora26 2022 files (not committed)
├── src/
│   ├── 01_load_eora.py      # load raw Eora matrices, build gross output + CO2
│   ├── 02_classical_mrio.py # regularise, solve full Leontief, bilateral footprints
│   ├── 03_build_subsystem.py# aggregate to the real 4-sector US-CHN subsystem
│   ├── 04_hhl_solve.py      # HHL quantum circuit, classical-vs-quantum comparison
│   ├── 05_make_figures.py   # result figures (minimalist, neutral blues)
│   └── 06_make_schematics.py# MRIO block + HHL pipeline schematics
├── results/
│   ├── FINAL_SUMMARY.json
│   ├── classical_summary.json
│   ├── sub4.npz             # the real 4-sector subsystem
│   └── hhl_final.npz        # quantum vs classical solution + metrics
├── figures/                 # all generated PNGs
└── paper/
    ├── main.tex             # IEEE-conference LaTeX source (ieeeconf class)
    ├── images/              # figures referenced by the paper
    └── main_preview.pdf     # compiled preview
```

---

## Reproducing the results

### 1. Environment

```bash
pip install -r requirements.txt
```

### 2. Data

The Eora26 2022 basic-price files are **not redistributed** here (see
`data/README.md` for licensing and download). Place the following in `data/`:

```
Eora26_2022_bp_T.txt    Eora26_2022_bp_FD.txt   Eora26_2022_bp_Q.txt
labels_T.txt            labels_FD.txt           labels_Q.txt
```

### 3. Run the pipeline

```bash
cd src
python 01_load_eora.py        # -> results/cache/*.npy
python 02_classical_mrio.py   # -> results/classical_summary.json
python 03_build_subsystem.py  # -> results/sub4.npz
python 04_hhl_solve.py        # -> results/hhl_final.npz
python 05_make_figures.py     # -> figures/*.png
python 06_make_schematics.py  # -> figures/fig_mrio_block.png, fig_hhl_pipeline.png
```

Or simply `make all` from the repo root.

## Method tl;dr

1. Build the Leontief system `(I − A) x = y` from
  Eora data, regularise the handful of non-viable data-artifact micro-sectors,
   invert, and compute the consumption-based footprint `E = eᵀ (I − A)⁻¹ y`.
2. Recast the same system (its 4-sector real aggregate)
   as a Hermitian linear-systems problem and solve it on an HHL circuit, reading
   the scalar emission aggregate `⟨e⟩` as a quantum expectation value.
3. Report agreement, characterise the residual error, and measure
   the condition number that governs scaling to the full system.

---

## Notes & honest limits

- The quantum demonstration runs on a **4-sector aggregate** of the real system,
  on a **statevector simulator**, not the full system on hardware. The claim is
  that HHL reproduces a real-data MRIO aggregate at small scale, plus a precise
  characterisation of what stands between this and full scale.
- Per Tang (2019) dequantisation results, an exponential advantage survives only
  if the Leontief matrix is genuinely high-rank; whether Eora is effectively
  low-rank is an open question this work frames but does not settle.

## Citation

If you use this code or data pipeline, please cite the accompanying paper
(`paper/main.tex`).
