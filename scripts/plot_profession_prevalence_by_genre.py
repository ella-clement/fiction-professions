import textwrap
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import rcParams
import config

df = pd.read_excel(os.path.join(config.DATA_DIR, 'profession_ranking_all_genres.xlsx'))

genre_columns = ["Contemporary fiction",
                "Fantasy",
                "Fantasy romance",
                "Historical fiction",
                "Horror",
                "Literary fiction",
                "Mystery",
                "Romance",
                "Science fiction",
                "Thriller"
                ]  

df = df[df["Label"].notna() & (df["Label"] != "Unknown") & (df["Label"] != "Other")].copy()

heatmap_data = df[["Label"] + genre_columns].set_index("Label")
heatmap_data = heatmap_data.div(heatmap_data.sum(axis=0), axis=1)

wrapped_columns = ['\n'.join(textwrap.wrap(col, 12)) for col in heatmap_data.columns]
heatmap_data.columns = wrapped_columns

# Figure config
# 190 mm = 7.48 inches wide (2-column layout)
fig_width = 7.48
fig_height = min(9, len(heatmap_data) * 0.25 + 1.0)

plt.rcParams["font.family"] = "Arial"
rcParams.update({
    'font.size': 7,
    'axes.labelsize': 7,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'lines.linewidth': 0.75,
    'axes.linewidth': 0.25
})

fig = plt.figure(figsize=(fig_width, fig_height))
gs = gridspec.GridSpec(1, 2, width_ratios=[20, 1], wspace=0.05)

ax = fig.add_subplot(gs[0])
cax = fig.add_subplot(gs[1])

sns.heatmap(
    heatmap_data,
    cmap="Greys",
    cbar_ax=cax,
    ax=ax,
    cbar_kws={'label': 'Proportion'},
    linewidths=0.1,
    linecolor='white'
)

ax.set_title("")
ax.set_xlabel("Genre")
ax.set_ylabel("Role")
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

print(f"Figure size (inches): {fig.get_size_inches()}")
fig.subplots_adjust(left=0.14, right=0.94, bottom=0.08, top=0.95, wspace=0.05)
plt.savefig(os.path.join(config.PLOTS_DIR, "profession_prevalence_by_genre.pdf"), dpi=600,format='pdf', bbox_inches='tight')
