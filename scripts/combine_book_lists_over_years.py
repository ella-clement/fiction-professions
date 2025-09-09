import os
import pandas as pd
import glob
import config

csv_files = [os.path.join(config.DATA_DIR, f"combined_books_list_{year}.csv") for year in list(range(2023,2025))]

# Read all CSV files into a single dataframe
df_list = [pd.read_csv(file) for file in csv_files]

# Concatenate all dataframes
combined_df = pd.concat(df_list, ignore_index=True)

# Remove duplicates based on all columns
combined_df = combined_df.drop_duplicates()

# Save the cleaned dataframe to a new CSV file
combined_df.to_csv(os.path.join(config.DATA_DIR, f"combined_books_list_all_years.csv"), index=False)

print("All CSV files combined and duplicates removed.")