import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from adjustText import adjust_text
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import rcParams
from scipy.stats import spearmanr, pearsonr
import config

# --- Settings ---
NUM_BOOKS = 773 # The number of books in realistic genres only
US_POP = 336_000_000
EPS = 1e-12

# Choose width: "double" -> 7.48 in (190 mm), "onehalf" -> 5.51 in (140 mm)
WIDTH_MODE = "double"
FIG_W = 7.48 if WIDTH_MODE == "double" else 5.51
FIG_H = 4.5  

# --- Style / fonts / lines ---
plt.rcParams["font.family"] = "Arial"
rcParams.update({
    "font.size": 7,
    "axes.labelsize": 7,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "pdf.fonttype": 42,  # keep text editable in PDF
    "ps.fonttype": 42,
    "axes.linewidth": 0.25,  # border lines
    "lines.linewidth": 1.0,  # prominent lines (trend/midlines)
})

# --- Load & prep ---
df = pd.read_excel(os.path.join(config.DATA_DIR, "profession_ranking_realistic_genres.xlsx"))
df = df[df["Profession"] != "Unknown"].copy()
df = df[df[["Normalized_Count", "Quantity", "Prestige"]].notna().all(axis=1)].copy()

df["Normalized_Fiction"] = df["Normalized_Count"] / NUM_BOOKS
df["Normalized_Real"] = df["Quantity"] / US_POP
df["Log_Fiction"] = np.log10(df["Normalized_Fiction"] + EPS)
df["Log_Real"] = np.log10(df["Normalized_Real"] + EPS)
df["Residual"] = df["Log_Fiction"] - df["Log_Real"]

prestige_df = pd.read_csv("occ_prestige_scores.csv")
avg_prestige = prestige_df["occ_prestige_title"].mean()

# Outlier selection by quadrant distance
df["distance"] = np.sqrt((df["Prestige"] - avg_prestige)**2 + (df["Residual"])**2)
q1 = df[(df["Prestige"] >= avg_prestige) & (df["Residual"] >= 0)]
q2 = df[(df["Prestige"] <  avg_prestige) & (df["Residual"] >= 0)]
q3 = df[(df["Prestige"] <  avg_prestige) & (df["Residual"] <  0)]
q4 = df[(df["Prestige"] >= avg_prestige) & (df["Residual"] <  0)]
annotate_df = pd.concat([q1.nlargest(5, "distance"),
                         q2.nlargest(5, "distance"),
                         q3.nlargest(5, "distance"),
                         q4.nlargest(5, "distance")])


# --- Correlation diagnostics: Prestige vs Residual ---
prestige = df["Prestige"].astype(float).to_numpy()
residual = df["Residual"].astype(float).to_numpy()

sr, sp = spearmanr(prestige, residual)
pr, pp = pearsonr(prestige, residual)

print("\n=== Correlation: Prestige vs Overrepresentation ===")
print(f"N occupations: {len(df)}")
print(f"Spearman ρ: {sr:.3f} (p={sp:.3g})")
print(f"Pearson r : {pr:.3f} (p={pp:.3g})\n")

# --- Plot ---
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))

# Salary data
df_salary = df[df["Salary"].notna()]
scatter = ax.scatter(
    df_salary["Prestige"], df_salary["Residual"],
    c=df_salary["Salary"], cmap="viridis",
    alpha=0.8, edgecolor="black", linewidth=0.25,
    label="With salary"
)

# No salary data → plot in grey
df_nosalary = df[df["Salary"].isna()]
ax.scatter(
    df_nosalary["Prestige"], df_nosalary["Residual"],
    color="#aaaaaa", alpha=0.7, edgecolor="black", linewidth=0.25,
    label="No salary"
)


# Trend line (black) and midlines (gray dashed)
sns.regplot(data=df, x="Prestige", y="Residual", scatter=False,
            line_kws=dict(color="black", alpha=0.9, linewidth=1.0),
            ci=None, ax=ax, truncate=False)

ax.axhline(0, color="gray", linestyle="--", linewidth=1.0)
ax.axvline(avg_prestige, color="gray", linestyle="--", linewidth=1.0)

# --- Manual annotation offsets: (dx, dy, ha, va) ---
# dx ~ 0.6 prestige units for horizontal moves
# dy ~ 0.08 residual units for vertical moves
manual_offsets = {
    "Hunter": (0, 0.08, "center", "bottom"),
    "Antique dealer": (-0.6, 0, "right", "center"),
    "Housekeeper": (0, 0.08, "center", "bottom"),
    "Bartender": (0, 0.08, "center", "bottom"),
    "Host": (0, 0.08, "center", "bottom"),
    "Medical examiner": (0, 0.08, "center", "bottom"),
    "Psychiatrist": (-0.6, 0.08, "right", "bottom"),
    "CEO": (0, -0.08, "center", "top"),
    "Architect": (0, 0.08, "center", "bottom"),
    "Doctor": (0, -0.08, "center", "top"),
    "Server": (0, -0.15, "center", "top"),
    "Barista": (0, 0.08, "center", "bottom"),
    "Dishwasher": (0.6, -0.08, "left", "top"),
    "Cashier": (0, -0.08, "center", "top"),
    "Groundskeeper/Janitor": (-0.6, 0, "right", "center"),
    "Pharmacist": (0, 0.03, "center", "bottom"),
    "Engineer": (0.6, 0, "left", "center"),
    "Tech executive": (0.6, 0, "left", "center"),
    "Hospital worker": (0, -0.08, "center", "top"),
    "Computer worker": (0.6, 0, "left", "center"),
}

# --- Manual annotation loop ---
for _, row in annotate_df.iterrows():
    label = row["Profession"]
    if label in manual_offsets:
        dx, dy, ha, va = manual_offsets[label]
        x, y = row["Prestige"], row["Residual"]
        x_text = x + dx
        y_text = y + dy

        ax.text(
            x_text, y_text, label,
            fontsize=7, ha=ha, va=va, alpha=0.9
        )
        ax.annotate(
            "", xy=(x, y), xytext=(x_text, y_text),
            arrowprops=dict(arrowstyle="-", color="gray", lw=0.5)
        )



# Quadrant labels @ 7 pt
x_min, x_max = ax.get_xlim()
y_min, y_max = ax.get_ylim()
x_off = (x_max - x_min) * 0.02
y_off = (y_max - y_min) * 0.02

ax.text(x_max - x_off, y_max - y_off, "High prestige\nOverrepresented",
        fontsize=7, ha="right", va="top", alpha=0.7)
ax.text(x_min + x_off, y_max - y_off, "Low prestige\nOverrepresented",
        fontsize=7, ha="left", va="top", alpha=0.7)
ax.text(x_min + x_off, y_min + y_off, "Low prestige\nUnderrepresented",
        fontsize=7, ha="left", va="bottom", alpha=0.7)
ax.text(x_max - x_off, y_min + y_off, "High prestige\nUnderrepresented",
        fontsize=7, ha="right", va="bottom", alpha=0.7)

divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="3%", pad=0.1)
cbar = fig.colorbar(scatter, cax=cax)
cbar.set_label("Hourly salary (USD)", fontsize=7)
cbar.ax.tick_params(labelsize=7)

ax.set_title("")  
ax.set_xlabel("Prestige score")
ax.set_ylabel("Log10(Fictional prevalence / Real-world prevalence)")

plt.tight_layout()
plt.savefig(os.path.join(config.PLOTS_DIR, "representation_vs_prestige.pdf"), dpi=600, format="pdf", bbox_inches="tight")
plt.show()