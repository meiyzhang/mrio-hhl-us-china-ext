"""
Regenerate all figures: minimalist, Times New Roman (Liberation Serif),
neutral-blue palette, terse titles/axes (detail goes in LaTeX captions).
"""
import numpy as np, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.font_manager as fm

# Register Liberation Serif (Times New Roman metric-compatible)
for p in ["/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
          "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
          "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"]:
    fm.fontManager.addfont(p)
rcParams['font.family'] = 'Liberation Serif'
rcParams['font.size'] = 12
rcParams['axes.linewidth'] = 0.6
rcParams['axes.edgecolor'] = '#33475b'
rcParams['xtick.color'] = '#33475b'
rcParams['ytick.color'] = '#33475b'
rcParams['text.color'] = '#1a2f4a'
rcParams['axes.labelcolor'] = '#1a2f4a'

# Neutral-blue palette
DEEP   = "#1f3a5f"   # deep navy blue
MID    = "#4a73a8"   # mid steel blue
LIGHT  = "#9bb8d6"   # light blue
PALE   = "#cdd9e8"   # pale blue-grey
ACCENT = "#2c5282"   # accent blue

def strip(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(length=3, width=0.6)

d   = np.load("../results/hhl_final.npz", allow_pickle=True)
sub = np.load("../results/sub4.npz", allow_pickle=True)
cs  = json.load(open("../results/classical_summary.json"))
r   = cs["results"]

# ───────────────────────── Fig 1: bilateral footprint ─────────────────────────
fig, ax = plt.subplots(figsize=(6.4, 3.8))
labels_ = ["US\u2192US", "US\u2192CN", "CN\u2192CN", "CN\u2192US"]
vals = [r["USA"]["domestic_Gt"], r["USA"]["in_other_Gt"],
        r["CHN"]["domestic_Gt"], r["CHN"]["in_other_Gt"]]
colors = [DEEP, MID, DEEP, MID]
bars = ax.bar(labels_, vals, color=colors, width=0.6, edgecolor='white', linewidth=0.5)
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v+0.07, f"{v:.2f}", ha='center',
            fontsize=11, color=DEEP)
ax.set_ylabel("Embodied CO$_2$ (Gt)")
ax.set_ylim(0, max(vals)*1.18)
strip(ax)
ax.grid(axis='y', alpha=0.25, linewidth=0.5, color=PALE)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("../figures/fig_bilateral_full.png", dpi=200, bbox_inches='tight')
plt.close()
print("fig_bilateral_full.png")

# ───────────────────────── Fig 2: classical vs HHL solution ───────────────────
groups = ["US-En", "US-NonEn", "CN-En", "CN-NonEn"]
x_cl = d["x_cl"]; x_h = d["x_hhl"]
fig, ax = plt.subplots(figsize=(6.4, 3.8))
w = 0.38; xp = np.arange(len(groups))
ax.bar(xp-w/2, x_cl/1e9, w, label="Classical", color=DEEP, edgecolor='white', linewidth=0.5)
ax.bar(xp+w/2, x_h/1e9,  w, label="HHL",       color=LIGHT, edgecolor='white', linewidth=0.5)
ax.set_xticks(xp); ax.set_xticklabels(groups)
ax.set_ylabel("Sector output ($\\times 10^{9}$ \\$)")
strip(ax)
ax.grid(axis='y', alpha=0.25, linewidth=0.5, color=PALE)
ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=11, loc='upper right')
plt.tight_layout()
plt.savefig("../figures/fig_solution_compare.png", dpi=200, bbox_inches='tight')
plt.close()
print("fig_solution_compare.png")

# ───────────────────────── Fig 3: policy number both ways ─────────────────────
fig, ax = plt.subplots(figsize=(4.2, 3.8))
vv = [d["E_cl"]/1e6, d["E_h"]/1e6]
bars = ax.bar(["Classical", "HHL"], vv, color=[DEEP, LIGHT], width=0.5,
              edgecolor='white', linewidth=0.5)
for b, v in zip(bars, vv):
    ax.text(b.get_x()+b.get_width()/2, v+0.06, f"{v:.2f}", ha='center',
            fontsize=11, color=DEEP)
ax.set_ylabel("Embodied CO$_2$ (Gt)")
ax.set_ylim(0, max(vv)*1.18)
strip(ax)
ax.grid(axis='y', alpha=0.25, linewidth=0.5, color=PALE)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("../figures/fig_policy_number.png", dpi=200, bbox_inches='tight')
plt.close()
print("fig_policy_number.png")

# ───────────────────────── Fig 4: complexity curves ──────────────────────────
fig, ax = plt.subplots(figsize=(6.0, 3.6))
N = np.logspace(1, 4, 200)
ax.loglog(N, N**3, color=DEEP, linewidth=1.6, label="Classical  $N^{3}$")
ax.loglog(N, np.log2(N), color=MID, linewidth=1.6, linestyle='--',
          label="HHL  $\\log N$")
ax.set_xlabel("System size $N$")
ax.set_ylabel("Relative cost")
strip(ax)
ax.grid(True, which='major', alpha=0.22, linewidth=0.5, color=PALE)
ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=11, loc='upper left')
plt.tight_layout()
plt.savefig("../figures/fig_complexity.png", dpi=200, bbox_inches='tight')
plt.close()
print("fig_complexity.png")

print("\nAll figures regenerated.")
