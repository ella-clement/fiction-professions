import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import rcParams
from scipy.stats import spearmanr, pearsonr
import config


# Load and clean data
df = pd.read_excel(os.path.join(config.DATA_DIR, "profession_ranking_realistic_genres.xlsx"))
df = df[df["Quantity"].notna() & df["Normalized_Count"].notna()].copy()
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
df["Normalized_Count"] = pd.to_numeric(df["Normalized_Count"], errors="coerce")
df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")
df = df[df["Quantity"].notna() & df["Normalized_Count"].notna()].copy()

US_POPULATION = 336_000_000
df["Normalized_Quantity"] = df["Quantity"] / US_POPULATION
df["Normalized_Fiction"] = df["Normalized_Count"] / 773

EPS = 1e-12
df["Log_Quantity"] = np.log10(df["Normalized_Quantity"] + EPS)
df["Log_Fiction"] = np.log10(df["Normalized_Fiction"] + EPS)
df["residual"] = df["Log_Fiction"] - df["Log_Quantity"]

# --- Correlation diagnostics ---
df_salary = df[df["Salary"].notna()].copy()
n = len(df_salary)

def _fmt(r, p):
    return f"{r:.3f} (p={p:.3g})"

if n >= 3:
    resid = df_salary["residual"].to_numpy()
    log_fiction = df_salary["Log_Fiction"].to_numpy()
    salary = df_salary["Salary"].astype(float).to_numpy()
    # Log-transform salary for robustness (heavy-tailed)
    log_salary = np.log10(np.clip(salary, 1e-6, None))

    # Salary vs overrepresentation (residual)
    sr_resid, sp_resid = spearmanr(salary, resid)
    pr_resid, pp_resid = pearsonr(salary, resid)
    # Robustness: use log10(salary)
    sr_resid_log, sp_resid_log = spearmanr(log_salary, resid)
    pr_resid_log, pp_resid_log = pearsonr(log_salary, resid)

    # Salary vs fictional prevalence level (not relative to real-world)
    sr_fic, sp_fic = spearmanr(salary, log_fiction)
    pr_fic, pp_fic = pearsonr(salary, log_fiction)

    print("\n=== Correlation checks for salary and representation ===")
    print(f"N occupations with salary: {n}")

    print("\n[Salary vs Overrepresentation] residual = Log_Fiction - Log_Quantity")
    print(f"  Spearman ρ: {_fmt(sr_resid, sp_resid)}")
    print(f"  Pearson r : {_fmt(pr_resid, pp_resid)}")
    print("  Robustness using log10(salary):")
    print(f"    Spearman ρ: {_fmt(sr_resid_log, sp_resid_log)}")
    print(f"    Pearson r : {_fmt(pr_resid_log, pp_resid_log)}")

    print("\n[Salary vs Fictional Prevalence] outcome = Log_Fiction")
    print(f"  Spearman ρ: {_fmt(sr_fic, sp_fic)}")
    print(f"  Pearson r : {_fmt(pr_fic, pp_fic)}\n")

else:
    print(f"\n=== Correlation checks skipped: too few observations with salary (N={n}) ===\n")


# Compute MAD-based shading
median_resid = np.median(df["residual"])
mad_resid = np.median(np.abs(df["residual"] - median_resid))
x_min = df["Log_Quantity"].min() - 0.2
x_max = df["Log_Quantity"].max() + 0.2
x_vals = np.linspace(x_min, x_max, 500)
identity = x_vals
lower_bound = identity + median_resid - mad_resid
upper_bound = identity + median_resid + mad_resid

# Set up plot parameters
plt.rcParams["font.family"] = "Arial"
rcParams.update({
    'font.size': 7,
    'axes.labelsize': 7,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 7,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'axes.linewidth': 0.25,
    'lines.linewidth': 1.0
})
fig, ax = plt.subplots(figsize=(7.48, 4.5)) 

# Plot identity line and shaded region
plt.plot(x_vals, identity, linestyle='dashed', color='gray', label="Equal representation (y = x)")
plt.fill_between(x_vals, lower_bound, upper_bound, color='gray', alpha=0.2,
                 label="Median ± MAD of residuals")

# Plot points with known salary
df_salary = df[df["Salary"].notna()]
scatter = plt.scatter(df_salary["Log_Quantity"], df_salary["Log_Fiction"],
                      c=df_salary["Salary"], cmap="viridis", alpha=0.8, edgecolor='black', label="With salary")

# Plot points with missing salary in grey
df_nosalary = df[df["Salary"].isna()]
plt.scatter(df_nosalary["Log_Quantity"], df_nosalary["Log_Fiction"],
            color='#aaaaaa', alpha=0.7, edgecolor='black', label="No salary")

plt.xlim(x_min, x_max)
y_min = df["Log_Fiction"].min() - 0.2
y_max = df["Log_Fiction"].max() + 0.2
plt.ylim(y_min, y_max)

# Annotate top over- and underrepresented jobs
top_over = df.nlargest(10, "residual")
top_under = df.nsmallest(5, "residual")


manual_offsets = {
    "Aristocrat": (0.1, 0.03, 'center', 'bottom'),
    "Royalty": (0.05, -0.03, 'left', 'top'),
    "Gig worker": (0.035, 0.03, 'center', 'bottom'), 
    "Astronaut": (-0.002, 0.03, 'right', 'bottom'),
    "Religious leader": (-0.08, 0, 'right', 'bottom'),
    "Athlete": (0, 0.03, 'left', 'bottom'),
    "Administrator": (0.03, -0.03, 'left', 'top'),
    "Retiree": (0, -0.0368, 'center', 'top'),
    "Writer": (-0.03, 0.03,	'right', 'bottom'),
    "Crypto miner": (0.1, 0, 'left', 'center'),
    "Assassin": (0, 0.03, 'center', 'bottom'),
    "Bounty hunter": (-0.1, 0, 'right', 'center'),
    "Secret agent": (-0.1, 0, 'right', 'center'),
    "Land owner": (0.03, -0.03, 'left', 'top'),
    "Handyperson": (0.1, 0, 'left', 'center'),
}

labelled_df = pd.concat([top_over, top_under])

for _, row in labelled_df.iterrows():
    label = row["Profession"] if pd.notna(row["Profession"]) else "Unknown"
    
    if label in manual_offsets:
        x, y = row["Log_Quantity"], row["Log_Fiction"]
        dx, dy, ha, va = manual_offsets[label]
        x_text = x + dx
        y_text = y + dy

        plt.text(
            x_text,
            y_text,
            label,
            fontsize=7,
            ha=ha, 
            va=va, 
            alpha=0.9
        )

        plt.annotate(
            "",  # no text
            xy=(x, y),  # point to
            xytext=(x_text, y_text),  # point from
            arrowprops=dict(
                arrowstyle='-',
                color='gray',
                lw=0.5,
                shrinkA=4,
                shrinkB=4,
            )
        )



plt.title("")
plt.xlabel("Real-world prevalence (base-10 log)")
plt.ylabel("Fiction prevalence (base-10 log)")
ax = plt.gca()
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="3%", pad=0.1)  
cbar = plt.colorbar(scatter, cax=cax)
cbar.set_label("Hourly salary (USD)")
cbar.ax.tick_params(labelsize=7)

handles, labels = ax.get_legend_handles_labels()
filtered = [(h, l) for h, l in zip(handles, labels) if l not in ["With salary", "No salary"]]
if filtered:
    handles, labels = zip(*filtered)
    ax.legend(handles, labels)
else:
    ax.legend().remove()  


plt.tight_layout()
plt.savefig(os.path.join(config.PLOTS_DIR, "real_world_prevalence.pdf"), dpi=600, format='pdf', bbox_inches='tight')





