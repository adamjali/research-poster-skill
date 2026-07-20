#!/usr/bin/env python
"""
WORKED EXAMPLE (image-chart path) for the research-poster skill. Generates the poster's charts as
high-DPI PNGs with matplotlib, for the "polished images" option (pixel-perfect: leader lines,
luminance-based label contrast, exact label text) at the cost of the charts not being editable in
PowerPoint. Fictional placeholder data. Copy and swap the DATA block + PALETTE.

Run:  python make_charts_example.py   ->  writes chart_availability.png, chart_modality.png, chart_barriers.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np, os, warnings
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
NAVY = "#1F3A5F"; GOLD = "#C9A24B"; GRAY = "#B9B9B2"; INK = "#1A1A1A"; SUB = "#4A4A45"
avail = {f.name for f in font_manager.fontManager.ttflist}
FAM = "Arial" if "Arial" in avail else ("Helvetica" if "Helvetica" in avail else "DejaVu Sans")
plt.rcParams.update({"font.family": FAM, "figure.facecolor": "white", "axes.facecolor": "white",
                     "savefig.facecolor": "white"}); DPI = 300

def lum(h):
    h = h.lstrip("#"); r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b

def donut(fname, title, sub, sizes, labels, colors, startangle=90):
    fig, ax = plt.subplots(figsize=(7.6, 7.4)); total = sum(sizes); W = 0.50
    wedges, _ = ax.pie(sizes, colors=colors, startangle=startangle, counterclock=False, radius=1.0,
                       wedgeprops=dict(width=W, edgecolor="white", linewidth=3.5))
    for w, s, c in zip(wedges, sizes, colors):
        ang = np.deg2rad((w.theta1 + w.theta2) / 2); cx, cy = np.cos(ang), np.sin(ang); p = round(s / total * 100)
        if p >= 15:                                     # inside, centered in the ring band
            col = "white" if lum(c) < 140 else INK
            ax.text((1 - W / 2) * cx, (1 - W / 2) * cy, f"{p}%", ha="center", va="center",
                    fontsize=44, fontweight="bold", color=col, clip_on=False)
        else:                                           # small slice: outside with a leader line
            ha = "center" if abs(cx) < 0.35 else ("left" if cx > 0 else "right")
            ax.annotate(f"{p}%", xy=(cx, cy), xytext=(1.30 * cx, 1.30 * cy), ha=ha, va="center",
                        fontsize=40, fontweight="bold", color=INK, clip_on=False,
                        arrowprops=dict(arrowstyle="-", color="#555", lw=2.4))
    ax.set_aspect("equal"); ax.set_xlim(-1.35, 1.35); ax.set_ylim(-1.25, 1.5)
    fig.suptitle(title, x=0.5, y=0.975, ha="center", fontsize=31, fontweight="bold", color=INK)
    fig.text(0.5, 0.905, sub, ha="center", va="top", fontsize=25, style="italic", color=SUB)
    ax.legend(wedges, labels, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=len(labels),
              frameon=False, fontsize=26, handlelength=1.1, columnspacing=1.6, handletextpad=0.5)
    fig.subplots_adjust(top=0.83, bottom=0.11, left=0.03, right=0.97)
    fig.savefig(os.path.join(HERE, fname), dpi=DPI); plt.close(fig); print("saved", fname)

def hbars(fname, title, sub, cats, vals, colors):
    fig, ax = plt.subplots(figsize=(15.5, 5.7)); y = list(range(len(cats)))[::-1]
    ax.barh(y, vals, color=colors, height=0.62, edgecolor="white")
    ax.set_yticks(y); ax.set_yticklabels(cats, fontsize=26, fontweight="bold", color=INK)
    ax.set_xlim(0, 70); ax.set_xticks([0, 20, 40, 60])
    ax.set_xticklabels([f"{t}%" for t in [0, 20, 40, 60]], fontsize=20, color=SUB)
    ax.xaxis.grid(True, color="#E2E1DA", linewidth=1.5); ax.set_axisbelow(True)
    for sp in ["top", "right", "left"]: ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color("#CFCEC6"); ax.tick_params(length=0)
    for yi, v in zip(y, vals):
        ax.text(v + 1.5, yi, f"{v:.0f}%", va="center", ha="left", fontsize=27, fontweight="bold", color=NAVY)
    fig.suptitle(title, x=0.015, y=0.985, ha="left", fontsize=31, fontweight="bold", color=INK)
    fig.text(0.015, 0.905, sub, ha="left", va="top", fontsize=25, style="italic", color=SUB)
    fig.subplots_adjust(top=0.83, bottom=0.12, left=0.30, right=0.985)
    fig.savefig(os.path.join(HERE, fname), dpi=DPI); plt.close(fig); print("saved", fname)

# fictional data, consistent with build_poster_example.py
donut("chart_availability.png", "Telehealth Availability", "n = 34 responding clinics",
      [28, 6], ["Offers telehealth (82%)", "None (18%)"], [NAVY, GRAY])
donut("chart_modality.png", "Primary Visit Modality", "n = 28 offering clinics",
      [17, 11], ["Video (61%)", "Phone (39%)"], [NAVY, GOLD], startangle=30)
hbars("chart_barriers.png", "Reported Barriers", "share of responding clinics (n = 34)",
      ["Broadband access", "Reimbursement", "Staff training"], [56, 44, 32], [NAVY, NAVY, GOLD])
print("charts done")
