"""Draw the concept illustrations used in the README (docs/img/*.png).

These are explanatory sketches, not data products. Where a number appears (dB levels, ENL), it comes from the
notebook's output for this scene and is hard-coded here with a comment.

Run:  uv run python docs/make_illustrations.py
"""
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle, Circle, Ellipse

OUT = Path(__file__).parent / "img"
OUT.mkdir(exist_ok=True)

INK = "#1f2933"
WATER = "#2b6cb0"
ICE = "#e8f1f8"
MYI = "#cfd8e3"
BEAM = "#f6ad55"
ECHO = "#c53030"
MUTED = "#718096"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11, "text.color": INK,
    "axes.edgecolor": INK, "savefig.facecolor": "white", "figure.facecolor": "white",
})


def arrow(ax, xy0, xy1, color=INK, lw=2.0, style="-|>", ms=14, ls="-", alpha=1.0):
    ax.add_patch(FancyArrowPatch(xy0, xy1, arrowstyle=style, mutation_scale=ms, color=color, lw=lw,
                                 linestyle=ls, alpha=alpha, shrinkA=0, shrinkB=0))


def save(fig, name):
    fig.savefig(OUT / name, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("wrote", OUT / name)


# ---------------------------------------------------------------------------------------------------------
# 1. Imaging geometry: side view (incidence angle, near/far range, 5 sub-swaths) + top view (why it's mirrored)
# ---------------------------------------------------------------------------------------------------------
def geometry():
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(14, 5.6), gridspec_kw={"width_ratios": [1.55, 1]})

    # --- side view ---
    ax.set_xlim(-1, 9.6); ax.set_ylim(-1.6, 7.2); ax.axis("off")
    ax.set_title("Side view: the radar looks sideways, not straight down", fontweight="bold", loc="left")
    sat = (1.0, 6.2)
    ax.add_patch(Rectangle((sat[0] - 0.35, sat[1] - 0.2), 0.7, 0.4, color=INK))
    ax.add_patch(Rectangle((sat[0] - 1.05, sat[1] - 0.08), 0.65, 0.16, color="#4a5568"))
    ax.add_patch(Rectangle((sat[0] + 0.4, sat[1] - 0.08), 0.65, 0.16, color="#4a5568"))
    ax.text(sat[0], sat[1] + 0.45, "Sentinel-1\n(~700 km up)", ha="center", va="bottom", fontsize=10)

    # drawn to the real incidence angles of this scene (flat-Earth sketch): 19° near range, 47° far range
    near, far = sat[0] + sat[1] * np.tan(np.radians(19)), sat[0] + sat[1] * np.tan(np.radians(47))
    ax.add_patch(Polygon([sat, (near, 0), (far, 0)], closed=True, color=BEAM, alpha=0.25, lw=0))
    ax.plot([sat[0], near], [sat[1], 0], color=BEAM, lw=1.5); ax.plot([sat[0], far], [sat[1], 0], color=BEAM, lw=1.5)
    ax.plot([sat[0], sat[0]], [sat[1], 0], color=MUTED, ls=":", lw=1.2)
    ax.text(sat[0] - 0.12, 2.6, "nadir", rotation=90, color=MUTED, ha="right", fontsize=9)

    # ground + sub-swaths
    ax.add_patch(Rectangle((-1, -0.35), 10.6, 0.35, color=ICE, ec=INK, lw=0.8))
    edges = np.linspace(near, far, 6)
    shades = ["#fbd38d", "#f6ad55", "#fbd38d", "#f6ad55", "#fbd38d"]
    for i in range(5):
        ax.add_patch(Rectangle((edges[i], -0.35), edges[i + 1] - edges[i], 0.35, color=shades[i], ec=INK, lw=0.6))
        ax.text((edges[i] + edges[i + 1]) / 2, -0.17, f"EW{i + 1}", ha="center", va="center", fontsize=9)
    ax.annotate("", (near, -0.75), (far, -0.75), arrowprops=dict(arrowstyle="<->", color=INK))
    ax.text((near + far) / 2, -1.05, "Extra Wide swath ≈ 400 km, built from 5 sub-swaths",
            ha="center", va="top", fontsize=10)
    ax.text(near, 0.25, "near range\n(steep, ≈19°)", ha="center", va="bottom", fontsize=9)
    ax.text(far, 0.25, "far range\n(oblique, ≈47°)", ha="center", va="bottom", fontsize=9)

    # incidence angle at one ground point
    gx = sat[0] + sat[1] * np.tan(np.radians(36))  # a point at θ = 36°
    ax.plot([sat[0], gx], [sat[1], 0], color=ECHO, lw=1.8)
    ax.plot([gx, gx], [0, 2.4], color=MUTED, ls="--", lw=1.2)
    ang_ray = np.degrees(np.arctan2(sat[1], sat[0] - gx))
    t = np.radians(np.linspace(90, ang_ray, 30))
    ax.plot(gx + 1.4 * np.cos(t), 1.4 * np.sin(t), color=ECHO, lw=1.5)
    ax.text(gx - 0.6, 1.6, "θ", color=ECHO, fontsize=15, fontweight="bold")
    ax.text(gx + 0.15, 2.5, "incidence angle θ:\nangle between the beam\nand the vertical", fontsize=9, va="bottom")

    # --- top view ---
    ax2.set_xlim(-3, 3); ax2.set_ylim(-3.3, 3.3); ax2.set_aspect("equal"); ax2.axis("off")
    ax2.set_title("Top view: why our image looks mirrored", fontweight="bold", loc="left")
    arrow(ax2, (0.3, 2.6), (0.3, -2.6), color=INK, lw=2.5)
    ax2.text(0.55, 2.45, "flight direction\n(descending = southward)", fontsize=9, va="top")
    ax2.add_patch(Rectangle((-2.7, -2.2), 2.5, 4.2, color=BEAM, alpha=0.3, lw=0))
    ax2.text(-1.45, 2.15, "imaged swath\n(to the satellite's right)", ha="center", va="bottom", fontsize=9)
    arrow(ax2, (0.0, 0), (-2.4, 0), color=ECHO, lw=1.8)
    ax2.text(-1.2, 0.18, "looks right = west", color=ECHO, ha="center", fontsize=9)
    # compass
    cx, cy = 2.2, -2.4
    arrow(ax2, (cx, cy - 0.35), (cx, cy + 0.55), lw=1.5, ms=10)
    ax2.text(cx, cy + 0.65, "N", ha="center", fontweight="bold")
    ax2.text(-2.7, -2.75, "image column 0 = nearest = EAST edge\nlast column = farthest = WEST edge\n"
             "→ east is on the LEFT of the image (mirrored vs. a map)", fontsize=9, va="top")
    save(fig, "geometry.png")


# ---------------------------------------------------------------------------------------------------------
# 2. Scattering mechanisms: what HH and HV "see" over four surfaces
# ---------------------------------------------------------------------------------------------------------
def scattering():
    # dB levels below are the k-means cluster centres from the notebook (Section 7), rounded.
    cases = [
        ("Calm open water", "mirror-like (specular):\nenergy bounces AWAY", WATER, "calm", "very dark", "very dark"),
        ("Wind-roughened water", "small waves scatter some\nenergy BACK", WATER, "rough", "bright (!)", "dark"),
        ("First-year ice", "salty: radar can't get in,\nfairly smooth surface", ICE, "fyi", "medium\n(≈ -16 dB)", "at noise floor\n(≈ -30 dB)"),
        ("Multi-year ice", "fresh, bubbly upper layer:\nwave bounces around INSIDE", MYI, "myi", "bright\n(≈ -12 dB)", "bright\n(≈ -21 dB)"),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(16, 5.2))
    rng = np.random.default_rng(3)
    for ax, (title, note, color, kind, hh, hv) in zip(axes, cases):
        ax.set_xlim(0, 10); ax.set_ylim(-3.6, 7); ax.axis("off")
        ax.set_title(title, fontweight="bold")
        # surface
        x = np.linspace(0, 10, 400)
        if kind == "calm":
            y = np.zeros_like(x)
        elif kind == "rough":
            y = 0.28 * np.sin(x * 4.2) + 0.12 * np.sin(x * 9.1)
        elif kind == "fyi":
            y = 0.06 * np.sin(x * 3.0)
        else:
            y = 0.18 * np.sin(x * 1.6) + 0.1 * np.sin(x * 5.3)
        depth = -1.2
        ax.fill_between(x, depth, y, color=color, ec=INK, lw=1)
        if kind == "myi":
            for _ in range(28):
                ax.add_patch(Circle((rng.uniform(0.6, 9.4), rng.uniform(-1.0, -0.15)), rng.uniform(0.05, 0.14),
                                    fc="white", ec=MUTED, lw=0.6))
        if kind == "fyi":
            ax.text(5, -0.65, "brine (salt) pockets", ha="center", fontsize=8, color=MUTED)

        # incoming beam from upper left
        hit = (5.0, 0.0)
        arrow(ax, (1.2, 5.2), hit, color=BEAM, lw=3)
        ax.text(1.0, 5.5, "radar pulse", color="#c05621", fontsize=9)
        back = dict(color=ECHO, lw=2.2)
        if kind == "calm":
            arrow(ax, hit, (8.8, 5.2), color=MUTED, lw=2.5, ls="--")
            ax.text(8.9, 5.5, "lost", color=MUTED, fontsize=9, ha="center")
        elif kind == "rough":
            arrow(ax, hit, (8.8, 4.6), color=MUTED, lw=2, ls="--")
            arrow(ax, hit, (2.4, 3.6), **back)
            arrow(ax, hit, (5.4, 3.0), color=ECHO, lw=1.2, alpha=0.6)
        elif kind == "fyi":
            arrow(ax, hit, (8.6, 4.8), color=MUTED, lw=2, ls="--")
            arrow(ax, hit, (3.0, 3.0), color=ECHO, lw=1.4)
        else:
            arrow(ax, hit, (2.4, 3.8), **back)
            # internal bounces
            pts = [(5.0, -0.1), (4.2, -0.7), (5.6, -0.95), (6.4, -0.4), (5.9, 0.0)]
            ax.plot(*zip(*pts), color=ECHO, lw=1.2)
            arrow(ax, (5.9, 0.0), (7.2, 3.4), color="#2f855a", lw=2.2)
            ax.text(7.3, 3.5, "polarization\nrotated → HV", color="#2f855a", fontsize=8.5)
        ax.text(5, -1.55, note, ha="center", va="top", fontsize=9.5)

        # HH / HV badges
        for i, (lab, val) in enumerate([("HH", hh), ("HV", hv)]):
            bx = 1.0 + i * 4.5
            dark = any(w in val for w in ("dark", "noise"))
            ax.add_patch(Rectangle((bx, -3.5), 3.8, 1.05, fc="#2d3748" if dark else "#f7fafc", ec=INK, lw=0.8))
            ax.text(bx + 1.9, -2.97, f"{lab}: {val}", ha="center", va="center", fontsize=8.5,
                    color="white" if dark else INK)
    fig.suptitle("What the radar sees: brightness depends on how the surface sends energy back",
                 fontweight="bold", fontsize=13, y=1.02)
    fig.text(0.5, -0.03, "HH = sent horizontal, received horizontal (surface roughness).   "
             "HV = sent horizontal, received vertical (needs multiple bounces, i.e. volume scattering).\n"
             "Wind-roughened water vs. ice in HH is the classic trap: HV breaks the tie, as long as it's above the noise floor.",
             ha="center", fontsize=10, color=MUTED)
    save(fig, "scattering.png")


# ---------------------------------------------------------------------------------------------------------
# 3. The dB ladder: measured class levels vs. the instrument noise floor
# ---------------------------------------------------------------------------------------------------------
def db_ladder():
    # Values from the notebook output for this scene:
    #   NESZ (noise floor): HH mean -29.2 dB, HV mean -29.8 dB, range about -32.6 to -25.4 dB  (Section 3)
    #   k-means k=4 centres (HH, HV): (-18.7,-35.1) (-16.2,-30.5) (-13.3,-27.4) (-11.5,-20.9) (Section 7)
    classes = [("dark leads\n(water / thin ice)", -18.7, -35.1, "#2b6cb0"),
               ("first-year ice", -16.2, -30.5, "#718096"),
               ("multi-year ice", -11.5, -20.9, "#2f855a")]
    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.axhspan(-32.6, -25.4, color="#fed7d7", alpha=0.8, lw=0)
    ax.axhline(-29.5, color=ECHO, lw=2)
    ax.text(2.48, -29.1, "instrument noise floor (NESZ ≈ -29.5 dB)\nsignal below this line is mostly noise",
            color=ECHO, fontsize=10, va="bottom", ha="right")
    for xi, pol in enumerate(["HH", "HV"]):
        for name, hh, hv, c in classes:
            v = hh if pol == "HH" else hv
            ax.plot([xi + 0.75, xi + 1.25], [v, v], color=c, lw=6, solid_capstyle="butt")
            ax.text(xi + 1.3, v, f"{name.splitlines()[0]}  {v:.0f} dB", va="center", fontsize=9.5, color=c)
    ax.set_xlim(0.5, 2.55); ax.set_ylim(-38, -8)
    ax.set_xticks([1, 2]); ax.set_xticklabels(["HH (co-pol)", "HV (cross-pol)"], fontsize=12)
    ax.set_ylabel("backscatter σ⁰ (dB)   ← darker     brighter →")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_title("Measured levels in this scene vs. the noise floor", fontweight="bold", loc="left")
    ax.text(0.52, -37.5, "Every 10 dB = 10× more power. HH is well above the noise everywhere; in HV only multi-year ice is.",
            fontsize=9.5, color=MUTED)
    save(fig, "db_ladder.png")


# ---------------------------------------------------------------------------------------------------------
# 4. Speckle: why a uniform surface looks grainy, and what averaging does
# ---------------------------------------------------------------------------------------------------------
def speckle():
    rng = np.random.default_rng(0)
    fig = plt.figure(figsize=(15, 3.9))
    gs = fig.add_gridspec(1, 5, width_ratios=[1.15, 1.05, 1, 1, 1], wspace=0.28)

    # (a) one pixel with many scatterers
    ax = fig.add_subplot(gs[0]); ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((1, 1), 8, 8, fc=ICE, ec=INK, lw=1.5))
    for _ in range(40):
        ax.add_patch(Ellipse((rng.uniform(1.5, 8.5), rng.uniform(1.5, 8.5)), rng.uniform(0.2, 0.6),
                             rng.uniform(0.15, 0.4), angle=rng.uniform(0, 180), fc="#a0aec0", ec="none"))
    ax.set_title("(a) one 40 m pixel holds\nmany tiny scatterers", fontsize=10.5)

    # (b) phasor sum: random walk
    ax = fig.add_subplot(gs[1]); ax.set_aspect("equal"); ax.axis("off")
    ph = rng.uniform(0, 2 * np.pi, 7)
    pts = np.vstack([[0, 0], np.cumsum(np.c_[np.cos(ph), np.sin(ph)], axis=0)])
    for p0, p1 in zip(pts[:-1], pts[1:]):
        arrow(ax, tuple(p0), tuple(p1), color=MUTED, lw=1.3, ms=9)
    arrow(ax, (0, 0), tuple(pts[-1]), color=ECHO, lw=2.5)
    ax.plot(0, 0, "o", color=INK, ms=5)
    ax.text(0.15, -0.35, "start", fontsize=8.5, color=INK)
    ax.annotate("total echo", xy=tuple(pts[-1] * 0.6), xytext=(0.05, 0.02), textcoords="axes fraction",
                color=ECHO, fontsize=9.5, arrowprops=dict(arrowstyle="-", color=ECHO, lw=0.8))
    pad = 1.2
    ax.set_xlim(pts[:, 0].min() - pad, pts[:, 0].max() + pad); ax.set_ylim(pts[:, 1].min() - pad, pts[:, 1].max() + pad)
    ax.set_title("(b) their echoes add with random\nphases: the total is random", fontsize=10.5)

    # (c-e) simulated uniform surface at increasing number of looks
    # ENL 10.7 is the product metadata; ≈ 7-17 after our 5x5 multilook was measured in the notebook (Section 4).
    truth = 0.03  # same sigma0 everywhere
    for k, (L, label) in enumerate([(1, "single look\n(ENL 1)"), (10.7, "as delivered\n(GRD, ENL ≈ 11)"),
                                    (250, "heavily averaged\n(ENL ≈ 250)")]):
        ax = fig.add_subplot(gs[2 + k])
        img = rng.gamma(L, truth / L, size=(80, 80))
        ax.imshow(10 * np.log10(img), cmap="gray", vmin=-25, vmax=-10)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"({'cde'[k]}) {label}", fontsize=10.5)
    fig.text(0.72, -0.02, "(c-e) the SAME perfectly uniform surface, simulated. Averaging more 'looks' trades resolution for smoothness.",
             ha="center", fontsize=9.5, color=MUTED)
    fig.suptitle("Speckle: graininess that comes from how coherent radar works, not from the surface",
                 fontweight="bold", fontsize=13, y=1.06)
    save(fig, "speckle.png")


if __name__ == "__main__":
    geometry()
    scattering()
    db_ladder()
    speckle()
