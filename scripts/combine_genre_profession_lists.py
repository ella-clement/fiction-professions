import os
import pandas as pd
import config

xlsx_files = ['contemporary_fiction.xlsx',
            # 'fantasy.xlsx',
            # 'historical_fiction.xlsx',
            'horror.xlsx',
            'literary_fiction.xlsx',
            'mystery.xlsx',
            # 'science_fiction.xlsx',
            'thriller.xlsx',
            # 'fantasy_romance.xlsx',
            'romance.xlsx',
                ]

column_names = ["Profession", "Raw_Count", "Normalized_Count"]

all_dfs = []

for file in xlsx_files:
    df = pd.read_excel(os.path.join(config.DATA_DIR, 'genres', file), header=None)
    df = df.iloc[:, :3]
    df.columns = column_names

    # Group within file (in case of duplicates)
    df = df.groupby("Profession", as_index=False).sum()
    
    all_dfs.append(df)

# Combine all DataFrames
combined_df = pd.concat(all_dfs, ignore_index=True)

# Group again to sum across files
final_df = combined_df.groupby("Profession", as_index=False).sum()

output_path = os.path.join(config.DATA_DIR, "profession_ranking_realistic_genres.xlsx")
final_df.to_excel(output_path, index=False)

print(f"Combined file saved to: {output_path}")
