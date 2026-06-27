# Eora26 2022 Data

The raw Eora26 input–output files are **not redistributed** in this repository
because the Eora MRIO database is released under its own license and the files
are large (the transaction matrix alone is ~277 MB). You must obtain them
directly from the source and place them in this `data/` directory before running
the pipeline.

## How to obtain

1. Visit the Eora global MRIO project: <https://worldmrio.com/eora26/>
2. Register for access (free for academic use) and download the **2022, basic
   prices** release of the 26-sector aggregation.
3. Place the following files in this directory:

```
data/
├── Eora26_2022_bp_T.txt     # 4915 × 4915 inter-industry transaction matrix Z
├── Eora26_2022_bp_FD.txt    # 4915 × 1140 final demand
├── Eora26_2022_bp_Q.txt     # 2728 × 4915 satellite stressor accounts
├── Eora26_2022_bp_VA.txt    # value-added (primary inputs) — optional
├── labels_T.txt             # country–sector labels for T
├── labels_FD.txt            # labels for final-demand columns
└── labels_Q.txt             # labels for satellite stressor rows
```

## File semantics

| File | Shape | Meaning |
|---|---|---|
| `Eora26_2022_bp_T.txt`  | 4915 × 4915 | Inter-industry transactions Z. Row/col 4915 is the `ROW TOTAL` aggregate; the first 4914 are real country–sector pairs (189 countries × 26 sectors). |
| `Eora26_2022_bp_FD.txt` | 4915 × 1140 | Final demand: 190 regions × 6 demand categories. |
| `Eora26_2022_bp_Q.txt`  | 2728 × 4915 | Satellite stressor accounts. The clean `I-GHG-CO2 emissions (Gg)` block spans label lines 10–64 (55 rows). |
| `labels_T.txt`          | 4915 rows   | `country  country  type  sector` per row. `type` is `Industries` or `Commodities` (some countries, e.g. CHN, use the commodity classification). |

## Validation

After running `src/01_load_eora.py`, the total global direct CO₂ should be
**≈ 33.3 Gt**, and the largest single emitters should be Chinese and US
electricity generation and US transport. If you see those, the data is loaded
correctly.

## Citation

> Lenzen, M., Moran, D., Kanemoto, K., Geschke, A. (2013). Building Eora: A
> Global Multi-regional Input–Output Database at High Country and Sector
> Resolution. *Economic Systems Research*, 25(1), 20–49.
