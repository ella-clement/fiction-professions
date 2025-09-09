import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams
import config

df = pd.read_excel(os.path.join(config.DATA_DIR, 'profession_ranking_all_genres.xlsx'))

df = df[df["Profession"] != "Unknown"].copy()
df = df[df["Label"] != "Other"].copy()
df = df[df["Label"].notna()]
df["Proportion"] = df["Normalized_Count"] / df["Normalized_Count"].sum()
df = df.sort_values(by="Proportion", ascending=False)

# Figure params
plt.rcParams["font.family"] = "Arial"
# Target single-column width: 90 mm = ~3.54 inches
fig_width = 3.54  # inches
fig_height = max(2.5, len(df) * 0.15)  # Adjust height to fit labels

rcParams.update({
    'font.size': 7,
    'axes.labelsize': 7,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 7,
    'pdf.fonttype': 42,  # TrueType fonts for editable text in PDF
    'ps.fonttype': 42,
    'lines.linewidth': 0.75,  # 0.75 pt line width for bar edges
    'axes.linewidth': 0.25    # for plot borders
})

colors = sns.color_palette("colorblind", n_colors=1)
bar_color = "#4D4D4D" 

fig, ax = plt.subplots(figsize=(fig_width, fig_height))
sns.barplot(data=df, y="Label", x="Proportion", color=bar_color, ax=ax)
ax.set_title("")
ax.set_xlabel("Proportion of books with role")
ax.set_ylabel("Role")
plt.tight_layout()
print(f"Figure size (inches): {fig.get_size_inches()}")
plt.savefig(os.path.join(config.PLOTS_DIR, "profession_prevalence_overall.pdf"), dpi=600, format='pdf')