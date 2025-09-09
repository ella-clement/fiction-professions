import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import config

# Target width in mm: choose 190 (2-col), 140 (1.5-col), or 90 (1-col)
TARGET_WIDTH_MM = 190
FIG_W_IN = TARGET_WIDTH_MM / 25.4  # mm -> inches
FIG_H_IN = 4.5                     

FONT_PT = 7                        
LW_THIN = 0.25  # thin linework per spec
LW_MAIN = 1.0   # “prominent” linework ~1pt

DIVERGING_CMAP = matplotlib.colormaps["BrBG"]
norm = Normalize(vmin=-5, vmax=5)

plt.rcParams.update({
    "font.family": "Arial",        
    "font.size": FONT_PT,
    "axes.labelsize": FONT_PT,
    "xtick.labelsize": FONT_PT,
    "ytick.labelsize": FONT_PT,
    "legend.fontsize": FONT_PT,
    "axes.linewidth": LW_THIN,     
})

# -------------------- Data processing --------------------
def process_file(filename, merge_royalty=True):
    df = pd.read_excel(filename)
    filtered = df[df["Male"] != "Unknown"].copy()

    if merge_royalty:
        royalty_rows = filtered["Male"].isin(["Emperor/Regent", "Prince/Princess"])
        if royalty_rows.any():
            cols = ["hetero_normalized", "male_normalized", "female_normalized"]
            royalty_agg = filtered.loc[royalty_rows, cols].fillna(0).sum()
            royalty_row = pd.DataFrame([{
                "Male": "Royalty",
                "hetero_normalized": royalty_agg["hetero_normalized"],
                "male_normalized": royalty_agg["male_normalized"],
                "female_normalized": royalty_agg["female_normalized"]
            }])
            filtered = pd.concat([filtered[~royalty_rows], royalty_row], ignore_index=True)

    total_male_known = filtered["male_normalized"].fillna(0).sum()
    total_female_known = filtered["female_normalized"].fillna(0).sum()
    filtered["male_normalized_adj"] = filtered["male_normalized"].fillna(0) / total_male_known
    filtered["female_normalized_adj"] = filtered["female_normalized"].fillna(0) / total_female_known

    filtered = filtered.sort_values("hetero_normalized", ascending=False).head(30)
    filtered["hetero_prop"] = filtered["hetero_normalized"] / filtered["hetero_normalized"].sum()

    epsilon = 1e-6
    male = filtered["male_normalized_adj"].fillna(0)
    female = filtered["female_normalized_adj"].fillna(0)
    filtered["log_ratio"] = np.log((male + epsilon) / (female + epsilon))
    filtered["log_ratio"] = filtered["log_ratio"].replace([np.inf, -np.inf], np.nan).fillna(0)
    filtered["log_ratio_clipped"] = filtered["log_ratio"].clip(-5, 5)

    return filtered.sort_values("hetero_prop", ascending=False).reset_index(drop=True)

romance   = process_file(os.path.join(config.DATA_DIR, 'genres', "romance.xlsx"),   merge_royalty=False)
romantasy = process_file(os.path.join(config.DATA_DIR, 'genres', "fantasy_romance.xlsx"), merge_royalty=True)

# -------------------- Plotting --------------------
fig, axes = plt.subplots(1, 2, figsize=(FIG_W_IN, FIG_H_IN), sharex=False, sharey=False, constrained_layout=True)

def plot_panel(ax, df, panel_label):
    colors = [DIVERGING_CMAP(norm(x)) for x in df["log_ratio_clipped"]]

    bars = ax.barh(
        y=df.index,
        width=df["hetero_prop"],
        color=colors,
        edgecolor="black",
        linewidth=LW_THIN
    )

    ax.set_yticks(df.index)
    ax.set_yticklabels(df["Male"])
    ax.set_ylim(-0.5, len(df) - 0.5)
    ax.invert_yaxis()

    ax.set_xlabel("Prevalence")

    # Light x-grid
    ax.grid(axis="x", linewidth=LW_THIN, linestyle=":", color="0.6")
    ax.tick_params(width=LW_THIN, length=3)

    ax.text(0.0, 1.02, panel_label, transform=ax.transAxes, va="bottom", ha="left",
            fontweight="bold")

plot_panel(axes[0], romance, "A")
axes[0].set_ylabel("Role")

plot_panel(axes[1], romantasy,   "B")
axes[1].set_ylabel("")

sm = cm.ScalarMappable(cmap=DIVERGING_CMAP, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=axes, pad=0.01, shrink=0.9)
cbar.set_label("Log(Male / Female prevalence)", labelpad=10)

# Make sure outer spines/ticks match line width spec
for ax in axes:
    for spine in ax.spines.values():
        spine.set_linewidth(LW_THIN)

plt.savefig(os.path.join(config.PLOTS_DIR, "romance_romantasy_prevalence.pdf"), format="pdf", dpi=600, bbox_inches="tight")
plt.show()
