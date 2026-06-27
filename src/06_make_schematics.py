"""
Two clean schematic figures for the methodology:
 (a) MRIO block-matrix structure
 (b) HHL pipeline (state prep -> QPE -> inversion -> uncompute -> measure)
Minimalist, neutral blues, Times New Roman (Liberation Serif).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import matplotlib.font_manager as fm

for p in ["/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
          "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
          "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"]:
    fm.fontManager.addfont(p)
rcParams['font.family'] = 'Liberation Serif'

DEEP="#1f3a5f"; MID="#4a73a8"; LIGHT="#9bb8d6"; PALE="#cdd9e8"; FILL="#e8eef6"

# ───────── (a) MRIO block structure ─────────
fig, ax = plt.subplots(figsize=(5.4, 4.0))
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')

# 2x2 region blocks of (I-A) Leontief matrix
shades = [[DEEP, LIGHT],[LIGHT, DEEP]]
labels = [["$Z_{US,US}$","$Z_{US,CN}$"],["$Z_{CN,US}$","$Z_{CN,CN}$"]]
x0, y0, s = 1.2, 4.2, 2.1
for i in range(2):
    for j in range(2):
        rx = x0 + j*s; ry = y0 + (1-i)*s
        ax.add_patch(Rectangle((rx, ry), s*0.96, s*0.96,
                     facecolor=(FILL if i==j else PALE),
                     edgecolor=DEEP, linewidth=1.0))
        ax.text(rx+s*0.48, ry+s*0.48, labels[i][j], ha='center', va='center',
                fontsize=11, color=DEEP)
# region labels
ax.text(x0+s*0.48, y0+2*s+0.35, "US", ha='center', fontsize=11, color=DEEP)
ax.text(x0+s*1.48, y0+2*s+0.35, "CN", ha='center', fontsize=11, color=DEEP)
ax.text(x0-0.45, y0+s*1.48, "US", va='center', ha='center', fontsize=11, color=DEEP, rotation=90)
ax.text(x0-0.45, y0+s*0.48, "CN", va='center', ha='center', fontsize=11, color=DEEP, rotation=90)
# equation underneath
ax.text(5.0, 2.4, r"$(\mathbf{I}-\mathbf{A})\,\mathbf{x} = \mathbf{y}$",
        ha='center', fontsize=15, color=DEEP)
ax.text(5.0, 1.3, r"$E = \mathbf{e}^{\top}(\mathbf{I}-\mathbf{A})^{-1}\mathbf{y}$",
        ha='center', fontsize=15, color=MID)
plt.tight_layout()
plt.savefig("../figures/fig_mrio_block.png", dpi=200, bbox_inches='tight')
plt.close()
print("fig_mrio_block.png")

# ───────── (b) HHL pipeline ─────────
fig, ax = plt.subplots(figsize=(7.2, 2.3))
ax.set_xlim(0, 10); ax.set_ylim(0, 3); ax.axis('off')
stages = [r"Encode $|b\rangle$", "QPE", r"Invert $1/\lambda$", "Uncompute", r"Measure $\langle e\rangle$"]
n = len(stages); bw = 1.55; gap = (10 - n*bw)/(n+1)
cols = [DEEP, MID, MID, MID, DEEP]
for k, (lab, c) in enumerate(zip(stages, cols)):
    bx = gap + k*(bw+gap)
    ax.add_patch(FancyBboxPatch((bx, 1.0), bw, 1.0,
                 boxstyle="round,pad=0.02,rounding_size=0.08",
                 facecolor=FILL, edgecolor=c, linewidth=1.2))
    ax.text(bx+bw/2, 1.5, lab, ha='center', va='center', fontsize=10.5, color=DEEP)
    if k < n-1:
        ax.add_patch(FancyArrowPatch((bx+bw, 1.5), (bx+bw+gap, 1.5),
                     arrowstyle='-|>', mutation_scale=11, color=MID, linewidth=1.0))
plt.tight_layout()
plt.savefig("../figures/fig_hhl_pipeline.png", dpi=200, bbox_inches='tight')
plt.close()
print("fig_hhl_pipeline.png")
